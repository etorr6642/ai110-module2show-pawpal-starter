"""Core domain objects for PawPal+: Task, Pet, Owner, and Scheduler."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
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
	last_completed_date: Optional[date] = None  # Date this task was last completed

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

	def is_due_today(self, today: Optional[date] = None) -> bool:
		"""
		Return True if this task should be performed today based on its frequency.

		DAILY and AS_NEEDED tasks are always due. WEEKLY tasks are due once 7 or
		more days have passed since last_completed_date, and MONTHLY tasks are due
		after 30 days. A task that has never been completed is always considered due.

		Args:
			today: The reference date to check against. Defaults to date.today().

		Returns:
			True if the task should appear in today's schedule, False otherwise.
		"""
		if today is None:
			today = date.today()
		if self.frequency in (Frequency.DAILY, Frequency.AS_NEEDED):
			return True
		if self.last_completed_date is None:
			return True  # Never completed — always due
		days_since = (today - self.last_completed_date).days
		if self.frequency == Frequency.WEEKLY:
			return days_since >= 7
		if self.frequency == Frequency.MONTHLY:
			return days_since >= 30
		return False

	def mark_completed(self) -> None:
		"""Mark task as completed and record today's date."""
		self.completed = True
		self.last_completed_date = date.today()

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

	def get_daily_tasks(self, today: Optional[date] = None) -> list[Task]:
		"""
		Get all tasks due today based on their frequency and last completion date.

		Delegates the due-date check to each Task's is_due_today method, so the
		result includes DAILY, AS_NEEDED, and any recurring tasks whose interval
		has elapsed.

		Args:
			today: The reference date passed through to is_due_today.
			       Defaults to date.today() if not provided.

		Returns:
			List of Task objects that are due for this pet today.
		"""
		return [task for task in self.tasks if task.is_due_today(today)]

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

	def get_all_daily_tasks(self, today: Optional[date] = None) -> list[tuple[Pet, Task]]:
		"""
		Return all tasks due today across all pets, deduplicated by task_id.

		If the same Task object is assigned to more than one pet, it is included
		only once (attributed to the first pet it is encountered on) to prevent
		double-counting time in the scheduler.

		Args:
			today: The reference date passed through to each pet's get_daily_tasks.
			       Defaults to date.today() if not provided.

		Returns:
			List of (Pet, Task) tuples for every unique task due today.
		"""
		seen_ids: set[str] = set()
		daily_tasks: list[tuple[Pet, Task]] = []
		for pet in self.pets:
			for task in pet.get_daily_tasks(today):
				if task.task_id not in seen_ids:
					seen_ids.add(task.task_id)
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

		Candidates are sorted by a three-part key: required tasks come before
		optional ones, then by priority descending, then by duration ascending
		(shorter tasks first when priority is tied). A greedy pass then takes
		each task in order if it fits in the remaining available minutes.

		Returns:
			List of (Pet, Task) tuples in the order they were scheduled.
			Tasks that did not fit within available_minutes_per_day are excluded.
		"""
		available = self.owner.available_minutes_per_day
		candidates = sorted(
			(pair for pair in self.owner.get_all_daily_tasks() if not pair[1].completed),
			key=lambda x: (not x[1].required, -x[1].priority, x[1].duration_minutes),
		)
		schedule = []
		for pet, task in candidates:
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
		summary = header + "\n".join(summary_lines)

		conflicts = self.detect_conflicts(schedule)
		if conflicts:
			conflict_block = "\n\nWarnings:\n" + "\n".join(f"  ! {c}" for c in conflicts)
			summary += conflict_block

		return summary

	def get_remaining_tasks(self, schedule: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
		"""Get tasks that didn't fit in the schedule."""
		scheduled_ids = {task.task_id for _, task in schedule}
		all_daily = self.owner.get_all_daily_tasks()
		return [
			(pet, task) for pet, task in all_daily
			if task.task_id not in scheduled_ids and not task.completed
		]

	def filter_by_pet(self, schedule: list[tuple[Pet, Task]], pet_id: str) -> list[tuple[Pet, Task]]:
		"""
		Return only the scheduled tasks belonging to a specific pet.

		Args:
			schedule: The list of (Pet, Task) tuples returned by generate_daily_schedule.
			pet_id:   The pet_id of the pet to filter for.

		Returns:
			Subset of schedule where every entry belongs to the given pet.
			Returns an empty list if the pet has no tasks in the schedule.
		"""
		return [(pet, task) for pet, task in schedule if pet.pet_id == pet_id]

	def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
		"""
		Return all tasks across all pets filtered by completion status.

		Searches every task on every pet, not just today's schedule, so completed
		recurring tasks from earlier in the day are included.

		Args:
			completed: Pass True to get completed tasks, False to get incomplete ones.

		Returns:
			List of (Pet, Task) tuples where task.completed matches the given value.
		"""
		return [
			(pet, task) for pet, task in self.owner.get_all_tasks()
			if task.completed == completed
		]

	def detect_conflicts(self, schedule: list[tuple[Pet, Task]]) -> list[str]:
		"""
		Detect scheduling conflicts and return them as human-readable warning strings.

		Checks for three conflict types:
		- Time slot: two or more different tasks for the same pet share the same
		  category (e.g., two morning tasks), reported with combined duration.
		- Duplicate: the same task description appears more than once for one pet.
		- Required task dropped: a required task exists but did not fit in the
		  schedule due to the owner's available time being exhausted.

		Args:
			schedule: The list of (Pet, Task) tuples returned by generate_daily_schedule.

		Returns:
			List of conflict description strings. Empty list means no conflicts found.
		"""
		conflicts: list[str] = []

		# Group tasks by (pet_id, category) to detect same-slot collisions
		slot_map: dict[tuple[str, str], list[tuple[Pet, Task]]] = defaultdict(list)
		pet_names: dict[str, str] = {}
		for pet, task in schedule:
			slot_map[(pet.pet_id, task.category)].append((pet, task))
			pet_names[pet.pet_id] = pet.name

		for (pet_id, category), entries in slot_map.items():
			if len(entries) > 1:
				task_names = ", ".join(f"'{t.description}'" for _, t in entries)
				total_slot_min = sum(t.duration_minutes for _, t in entries)
				conflicts.append(
					f"Time slot conflict for {pet_names[pet_id]}: "
					f"{task_names} are both scheduled in the {category} slot "
					f"({total_slot_min} min combined)"
				)

		# Check for duplicate task descriptions per pet
		pet_descriptions: dict[str, list[str]] = defaultdict(list)
		for pet, task in schedule:
			pet_descriptions[pet.pet_id].append(task.description)

		for pet_id, descriptions in pet_descriptions.items():
			seen: set[str] = set()
			for desc in descriptions:
				if desc in seen:
					conflicts.append(
						f"Duplicate task '{desc}' scheduled for {pet_names[pet_id]}"
					)
				seen.add(desc)

		# Check if total scheduled time exceeds owner's available minutes
		total_scheduled = sum(task.duration_minutes for _, task in schedule)
		if total_scheduled > self.owner.available_minutes_per_day:
			conflicts.append(
				f"Total scheduled time ({total_scheduled} min) exceeds available time "
				f"({self.owner.available_minutes_per_day} min)"
			)

		# Check if any required tasks were left out due to time
		remaining_required = [
			t for _, t in self.get_remaining_tasks(schedule) if t.required
		]
		if remaining_required:
			names = ", ".join(f"'{t.description}'" for t in remaining_required)
			conflicts.append(f"Required task(s) didn't fit in schedule: {names}")

		return conflicts

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