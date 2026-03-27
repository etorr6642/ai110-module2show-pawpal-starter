"""Core domain objects for PawPal+: Task, Pet, Owner, and Scheduler."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4
from enum import Enum


class Frequency(Enum):
	"""Task recurrence frequency."""
	DAILY = "daily"
	WEEKLY = "weekly"
	MONTHLY = "monthly"
	AS_NEEDED = "as_needed"


@dataclass
class Task:
	"""Represents a single pet-care activity."""

	description: str
	duration_minutes: int  # Time required to complete task
	frequency: Frequency  # How often task should be done
	priority: int  # 1-5, higher = more important
	category: str  # (e.g., "feeding", "walking", "grooming", "medication")
	task_id: str = field(default_factory=lambda: str(uuid4()))
	completed: bool = False  # Completion status for today
	required: bool = True  # If False, task can be skipped if time is tight

	MIN_PRIORITY = 1
	MAX_PRIORITY = 5

	def __post_init__(self) -> None:
		"""Validate task attributes on creation."""
		self._validate_duration(self.duration_minutes)
		self._validate_priority(self.priority)

	@classmethod
	def _validate_duration(cls, duration: int) -> None:
		"""Raise ValueError if duration is negative."""
		if duration < 0:
			raise ValueError("duration_minutes must be non-negative")

	@classmethod
	def _validate_priority(cls, priority: int) -> None:
		"""Raise ValueError if priority is outside the allowed range."""
		if not (cls.MIN_PRIORITY <= priority <= cls.MAX_PRIORITY):
			raise ValueError(
				f"priority must be between {cls.MIN_PRIORITY} and {cls.MAX_PRIORITY}"
			)

	def mark_completed(self) -> None:
		"""Mark task as completed."""
		self.completed = True

	def mark_incomplete(self) -> None:
		"""Mark task as incomplete."""
		self.completed = False

	def update_priority(self, new_priority: int) -> None:
		"""Update task priority with validation."""
		self._validate_priority(new_priority)
		self.priority = new_priority

	def update_duration(self, new_duration: int) -> None:
		"""Update task duration with validation."""
		self._validate_duration(new_duration)
		self.duration_minutes = new_duration


@dataclass
class Pet:
	"""Represents a pet with associated tasks."""

	name: str
	breed: str
	pet_type: str  # (e.g., "dog", "cat", "bird")
	tasks: list[Task] = field(default_factory=list)
	pet_id: str = field(default_factory=lambda: str(uuid4()))

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet's task list."""
		self.tasks.append(task)

	def remove_task(self, task_id: str) -> bool:
		"""Remove a task by ID. Return True if successful."""
		for index, task in enumerate(self.tasks):
			if task.task_id == task_id:
				del self.tasks[index]
				return True
		return False

	def get_task(self, task_id: str) -> Optional[Task]:
		"""Retrieve a task by ID."""
		for task in self.tasks:
			if task.task_id == task_id:
				return task
		return None

	def get_daily_tasks(self) -> list[Task]:
		"""Get all tasks scheduled for today (daily or as-needed)."""
		return [
			task for task in self.tasks
			if task.frequency == Frequency.DAILY or task.frequency == Frequency.AS_NEEDED
		]

	def get_completed_tasks(self) -> list[Task]:
		"""Get all tasks that have been marked completed."""
		return [task for task in self.tasks if task.completed]

	def get_incomplete_tasks(self) -> list[Task]:
		"""Get all tasks that are not yet completed."""
		return [task for task in self.tasks if not task.completed]

	def get_required_tasks(self) -> list[Task]:
		"""Get all required tasks for this pet."""
		return [task for task in self.tasks if task.required]


class Owner:
	"""Manages multiple pets and provides access to all their tasks."""

	def __init__(
		self,
		name: str,
		email: str,
		available_minutes_per_day: int,
	) -> None:
		"""Initialize an Owner with contact info and daily time budget."""
		self.name = name
		self.email = email
		self.available_minutes_per_day = available_minutes_per_day
		self.pets: list[Pet] = []
		self.owner_id: str = str(uuid4())

	def add_pet(self, pet: Pet) -> None:
		"""Add a new pet."""
		self.pets.append(pet)

	def remove_pet(self, pet_id: str) -> bool:
		"""Remove a pet by ID."""
		for index, pet in enumerate(self.pets):
			if pet.pet_id == pet_id:
				del self.pets[index]
				return True
		return False

	def get_pet(self, pet_id: str) -> Optional[Pet]:
		"""Retrieve a pet by ID."""
		for pet in self.pets:
			if pet.pet_id == pet_id:
				return pet
		return None

	def get_all_tasks(self) -> list[tuple[Pet, Task]]:
		"""Return all tasks across all pets as (pet, task) tuples."""
		all_tasks = []
		for pet in self.pets:
			for task in pet.tasks:
				all_tasks.append((pet, task))
		return all_tasks

	def get_all_daily_tasks(self) -> list[tuple[Pet, Task]]:
		"""Return all daily/as-needed tasks across all pets as (pet, task) tuples."""
		daily_tasks = []
		for pet in self.pets:
			for task in pet.get_daily_tasks():
				daily_tasks.append((pet, task))
		return daily_tasks

	def get_incomplete_tasks(self) -> list[tuple[Pet, Task]]:
		"""Return all incomplete tasks across all pets."""
		incomplete = []
		for pet in self.pets:
			for task in pet.get_incomplete_tasks():
				incomplete.append((pet, task))
		return incomplete

	def set_available_time(self, minutes: int) -> None:
		"""Update available time per day with validation."""
		if minutes < 0:
			raise ValueError("available_minutes_per_day must be non-negative")
		self.available_minutes_per_day = minutes


class Scheduler:
	"""The brain that retrieves, organizes, and manages tasks across pets."""

	def __init__(self, owner: Owner) -> None:
		"""Initialize the Scheduler with the Owner whose pets will be scheduled."""
		self.owner = owner

	def generate_daily_schedule(self) -> list[tuple[Pet, Task]]:
		"""
		Generate an optimized daily schedule that fits within available time.
		Prioritizes: required tasks > high priority > frequent tasks.
		Returns list of (pet, task) tuples in scheduled order.
		"""
		available = self.owner.available_minutes_per_day
		daily_tasks = self.owner.get_all_daily_tasks()

		# Separate required and optional
		required = [
			(pet, task) for pet, task in daily_tasks
			if task.required and not task.completed
		]
		optional = [
			(pet, task) for pet, task in daily_tasks
			if not task.required and not task.completed
		]

		# Sort by priority (descending)
		required.sort(key=lambda x: x[1].priority, reverse=True)
		optional.sort(key=lambda x: x[1].priority, reverse=True)

		# Greedy fit: try required first, then optional
		schedule = []
		for pet, task in required + optional:
			if task.duration_minutes <= available:
				schedule.append((pet, task))
				available -= task.duration_minutes

		return schedule

	def get_schedule_summary(self, schedule: list[tuple[Pet, Task]]) -> str:
		"""Generate a human-readable summary of the schedule."""
		if not schedule:
			return (
				f"No tasks fit in {self.owner.available_minutes_per_day} available minutes. "
				"Consider extending available time or deferring lower-priority tasks."
			)

		summary_lines = []
		total_time = 0
		for pet, task in schedule:
			summary_lines.append(
				f"• {pet.name}: {task.description} ({task.duration_minutes} min, priority {task.priority})"
			)
			total_time += task.duration_minutes

		header = f"Scheduled {len(schedule)} tasks for {total_time} minutes:\n"
		return header + "\n".join(summary_lines)

	def get_remaining_tasks(self, schedule: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
		"""Get tasks that didn't fit in the schedule."""
		scheduled_ids = {task.task_id for _, task in schedule}
		all_daily = self.owner.get_all_daily_tasks()
		return [
			(pet, task) for pet, task in all_daily
			if task.task_id not in scheduled_ids and not task.completed
		]

	def mark_task_complete(self, task_id: str) -> bool:
		"""Mark a task as completed. Return True if successful."""
		for pet in self.owner.pets:
			task = pet.get_task(task_id)
			if task:
				task.mark_completed()
				return True
		return False

	def get_pet_summary(self, pet: Pet) -> str:
		"""Get a summary of a pet's task status."""
		incomplete = pet.get_incomplete_tasks()
		completed = pet.get_completed_tasks()
		total_minutes = sum(t.duration_minutes for t in incomplete)
		return (
			f"{pet.name} ({pet.pet_type}):\n"
			f"  Completed: {len(completed)}/{len(pet.tasks)}\n"
			f"  Remaining time needed: {total_minutes} minutes"
		)