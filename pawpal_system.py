"""Core domain objects and planner skeleton for PawPal+."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class Pet:
	"""Represents the owner's pet profile."""

	name: str
	breed: str
	type: str

	def get_name(self) -> str:
		return self.name

	def set_name(self, name: str) -> None:
		self.name = name

	def get_breed(self) -> str:
		return self.breed

	def set_breed(self, breed: str) -> None:
		self.breed = breed

	def get_type(self) -> str:
		return self.type

	def set_type(self, pet_type: str) -> None:
		self.type = pet_type


@dataclass
class Task:
	"""Represents a pet-care task that can be scheduled."""

	name: str
	priority: int
	duration: int
	category: str
	required: bool = True
	pet_name: Optional[str] = None
	task_id: str = field(default_factory=lambda: str(uuid4()))

	MIN_PRIORITY = 1
	MAX_PRIORITY = 5

	def __post_init__(self) -> None:
		self._validate_duration(self.duration)
		self._validate_priority(self.priority)

	@classmethod
	def _validate_duration(cls, duration: int) -> None:
		if duration < 0:
			raise ValueError("duration must be non-negative")

	@classmethod
	def _validate_priority(cls, priority: int) -> None:
		if not (cls.MIN_PRIORITY <= priority <= cls.MAX_PRIORITY):
			raise ValueError(
				f"priority must be between {cls.MIN_PRIORITY} and {cls.MAX_PRIORITY}"
			)

	def get_task_id(self) -> str:
		return self.task_id

	def set_task_id(self, task_id: str) -> None:
		self.task_id = task_id

	def get_name(self) -> str:
		return self.name

	def set_name(self, name: str) -> None:
		self.name = name

	def get_priority(self) -> int:
		return self.priority

	def set_priority(self, priority: int) -> None:
		self._validate_priority(priority)
		self.priority = priority

	def get_duration(self) -> int:
		return self.duration

	def set_duration(self, duration: int) -> None:
		self._validate_duration(duration)
		self.duration = duration

	def get_category(self) -> str:
		return self.category

	def set_category(self, category: str) -> None:
		self.category = category

	def is_required(self) -> bool:
		return self.required

	def set_required(self, required: bool) -> None:
		self.required = required

	def get_pet_name(self) -> Optional[str]:
		return self.pet_name

	def set_pet_name(self, pet_name: Optional[str]) -> None:
		self.pet_name = pet_name


class User:
	"""Represents an owner profile and available daily planning constraints."""

	def __init__(
		self,
		name: str,
		email: str,
		password: str,
		available_minutes_per_day: int,
		pet: Optional[Pet] = None,
	) -> None:
		self.name = name
		self.email = email
		self.password = password
		self.available_minutes_per_day = available_minutes_per_day
		self.pet = pet

	def get_name(self) -> str:
		return self.name

	def set_name(self, name: str) -> None:
		self.name = name

	def get_email(self) -> str:
		return self.email

	def set_email(self, email: str) -> None:
		self.email = email

	def get_password(self) -> str:
		return self.password

	def set_password(self, password: str) -> None:
		self.password = password

	def get_available_minutes_per_day(self) -> int:
		return self.available_minutes_per_day

	def set_available_minutes_per_day(self, minutes: int) -> None:
		if minutes < 0:
			raise ValueError("available_minutes_per_day must be non-negative")
		self.available_minutes_per_day = minutes

	def update_available_time(self, minutes: int) -> None:
		if minutes < 0:
			raise ValueError("available_minutes_per_day must be non-negative")
		self.available_minutes_per_day = minutes

	def get_pet(self) -> Optional[Pet]:
		return self.pet

	def set_pet(self, pet: Pet) -> None:
		self.pet = pet


class Planner:
	"""Holds tasks and provides schedule-generation hooks."""

	def __init__(self, user: User) -> None:
		self.user = user
		self.tasks: list[Task] = []

	def get_user(self) -> User:
		return self.user

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)

	def edit_task(self, task_name: str, updated_fields: dict) -> bool:
		for task in self.tasks:
			if task.name == task_name:
				for field_name, value in updated_fields.items():
					if hasattr(task, field_name):
						setattr(task, field_name, value)
				return True
		return False

	def remove_task(self, task_name: str) -> bool:
		for index, task in enumerate(self.tasks):
			if task.name == task_name:
				del self.tasks[index]
				return True
		return False

	def generate_daily_plan(self) -> list[Task]:
		"""Return a plan that places required tasks first, then optional by priority."""
		remaining = self.user.available_minutes_per_day
		selected_tasks: list[Task] = []

		required_tasks = sorted(
			[task for task in self.tasks if task.required],
			key=lambda t: t.priority,
			reverse=True,
		)
		optional_tasks = sorted(
			[task for task in self.tasks if not task.required],
			key=lambda t: t.priority,
			reverse=True,
		)

		sorted_tasks = required_tasks + optional_tasks
		for task in sorted_tasks:
			if task.duration <= remaining:
				selected_tasks.append(task)
				remaining -= task.duration

		return selected_tasks

	def explain_plan(self, plan: list[Task]) -> str:
		"""Human-readable placeholder explanation for current scheduling approach."""
		if not plan:
			return (
				f"No tasks fit in {self.user.available_minutes_per_day} available minutes "
				"based on current priorities and durations."
			)

		task_names = ", ".join(task.name for task in plan)
		return (
			"Selected required tasks first, then highest-priority optional tasks within "
			f"{self.user.available_minutes_per_day} minutes: {task_names}."
		)