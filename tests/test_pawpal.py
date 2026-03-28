from datetime import date, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, Frequency


def make_task():
    return Task(
        description="Test task",
        duration_minutes=10,
        frequency=Frequency.DAILY,
        priority=3,
        category="morning",
    )


def test_mark_completed_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", breed="Labrador", pet_type="dog")
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_invalid_priority_raises():
    with pytest.raises(ValueError):
        Task(description="Bad", duration_minutes=10, frequency=Frequency.DAILY,
             priority=0, category="feeding")


def test_invalid_priority_too_high_raises():
    with pytest.raises(ValueError):
        Task(description="Bad", duration_minutes=10, frequency=Frequency.DAILY,
             priority=6, category="feeding")


def test_negative_duration_raises():
    with pytest.raises(ValueError):
        Task(description="Bad", duration_minutes=-1, frequency=Frequency.DAILY,
             priority=3, category="feeding")


def test_zero_duration_is_valid():
    task = Task(description="Check water", duration_minutes=0,
                frequency=Frequency.DAILY, priority=1, category="feeding")
    assert task.duration_minutes == 0


# ---------------------------------------------------------------------------
# Recurrence logic — is_due_today
# ---------------------------------------------------------------------------

def test_never_completed_task_is_always_due():
    task = Task(description="Walk", duration_minutes=20, frequency=Frequency.WEEKLY,
                priority=3, category="exercise")
    assert task.last_completed_date is None
    assert task.is_due_today(date.today()) is True


def test_weekly_task_not_due_before_7_days():
    task = Task(description="Bath", duration_minutes=30, frequency=Frequency.WEEKLY,
                priority=2, category="grooming")
    task.last_completed_date = date.today() - timedelta(days=6)
    assert task.is_due_today(date.today()) is False


def test_weekly_task_due_on_day_7():
    task = Task(description="Bath", duration_minutes=30, frequency=Frequency.WEEKLY,
                priority=2, category="grooming")
    task.last_completed_date = date.today() - timedelta(days=7)
    assert task.is_due_today(date.today()) is True


def test_monthly_task_not_due_before_30_days():
    task = Task(description="Vet checkup", duration_minutes=60,
                frequency=Frequency.MONTHLY, priority=5, category="medical")
    task.last_completed_date = date.today() - timedelta(days=29)
    assert task.is_due_today(date.today()) is False


def test_monthly_task_due_on_day_30():
    task = Task(description="Vet checkup", duration_minutes=60,
                frequency=Frequency.MONTHLY, priority=5, category="medical")
    task.last_completed_date = date.today() - timedelta(days=30)
    assert task.is_due_today(date.today()) is True


def test_as_needed_task_is_always_due():
    task = Task(description="Extra treat", duration_minutes=5,
                frequency=Frequency.AS_NEEDED, priority=1, category="feeding")
    task.last_completed_date = date.today()  # completed today — still due
    assert task.is_due_today(date.today()) is True


def test_mark_complete_then_daily_task_due_next_day():
    """Marking a daily task complete today means it is still due tomorrow."""
    task = Task(description="Feed", duration_minutes=5, frequency=Frequency.DAILY,
                priority=3, category="feeding")
    task.mark_completed()
    tomorrow = date.today() + timedelta(days=1)
    assert task.is_due_today(tomorrow) is True


# ---------------------------------------------------------------------------
# Sorting correctness — generate_daily_schedule
# ---------------------------------------------------------------------------

def _make_owner_with_tasks(tasks: list, available_minutes: int = 120) -> tuple:
    owner = Owner(name="Alex", email="alex@example.com",
                  available_minutes_per_day=available_minutes)
    pet = Pet(name="Buddy", breed="Labrador", pet_type="dog")
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    return scheduler, pet


def test_required_tasks_scheduled_before_optional():
    optional = Task(description="Play fetch", duration_minutes=15,
                    frequency=Frequency.DAILY, priority=5, category="exercise",
                    required=False)
    required = Task(description="Give medication", duration_minutes=5,
                    frequency=Frequency.DAILY, priority=2, category="medical",
                    required=True)
    scheduler, _ = _make_owner_with_tasks([optional, required])
    schedule = scheduler.generate_daily_schedule()
    descriptions = [t.description for _, t in schedule]
    assert descriptions.index("Give medication") < descriptions.index("Play fetch")


def test_higher_priority_scheduled_first_among_required():
    low = Task(description="Brush teeth", duration_minutes=10,
               frequency=Frequency.DAILY, priority=2, category="grooming")
    high = Task(description="Feed breakfast", duration_minutes=10,
                frequency=Frequency.DAILY, priority=5, category="feeding")
    scheduler, _ = _make_owner_with_tasks([low, high])
    schedule = scheduler.generate_daily_schedule()
    descriptions = [t.description for _, t in schedule]
    assert descriptions.index("Feed breakfast") < descriptions.index("Brush teeth")


def test_shorter_task_scheduled_first_when_priority_tied():
    longer = Task(description="Long walk", duration_minutes=30,
                  frequency=Frequency.DAILY, priority=3, category="exercise")
    shorter = Task(description="Quick walk", duration_minutes=10,
                   frequency=Frequency.DAILY, priority=3, category="exercise")
    scheduler, _ = _make_owner_with_tasks([longer, shorter])
    schedule = scheduler.generate_daily_schedule()
    descriptions = [t.description for _, t in schedule]
    assert descriptions.index("Quick walk") < descriptions.index("Long walk")


def test_task_excluded_when_no_time_remaining():
    big = Task(description="Long groom", duration_minutes=60,
               frequency=Frequency.DAILY, priority=3, category="grooming")
    scheduler, _ = _make_owner_with_tasks([big], available_minutes=30)
    schedule = scheduler.generate_daily_schedule()
    assert len(schedule) == 0


def test_task_included_when_duration_exactly_equals_available():
    exact = Task(description="Exact fit", duration_minutes=30,
                 frequency=Frequency.DAILY, priority=3, category="feeding")
    scheduler, _ = _make_owner_with_tasks([exact], available_minutes=30)
    schedule = scheduler.generate_daily_schedule()
    assert len(schedule) == 1


# ---------------------------------------------------------------------------
# Deduplication — shared Task object on two pets
# ---------------------------------------------------------------------------

def test_shared_task_appears_only_once_in_daily_schedule():
    shared_task = Task(description="Shared walk", duration_minutes=20,
                       frequency=Frequency.DAILY, priority=3, category="exercise")
    owner = Owner(name="Sam", email="sam@example.com", available_minutes_per_day=120)
    pet1 = Pet(name="Rex", breed="Poodle", pet_type="dog")
    pet2 = Pet(name="Fido", breed="Beagle", pet_type="dog")
    pet1.add_task(shared_task)
    pet2.add_task(shared_task)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_daily_schedule()
    assert len(schedule) == 1


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflict_detected_for_duplicate_category_same_pet():
    t1 = Task(description="Morning feed", duration_minutes=10,
              frequency=Frequency.DAILY, priority=3, category="feeding")
    t2 = Task(description="Evening feed", duration_minutes=10,
              frequency=Frequency.DAILY, priority=3, category="feeding")
    scheduler, _ = _make_owner_with_tasks([t1, t2])
    schedule = scheduler.generate_daily_schedule()
    conflicts = scheduler.detect_conflicts(schedule)
    assert any("feeding" in c and "Time slot conflict" in c for c in conflicts)


def test_conflict_detected_for_duplicate_description_same_pet():
    t1 = Task(description="Feed dog", duration_minutes=10,
              frequency=Frequency.DAILY, priority=3, category="feeding")
    t2 = Task(description="Feed dog", duration_minutes=10,
              frequency=Frequency.DAILY, priority=3, category="morning")
    scheduler, _ = _make_owner_with_tasks([t1, t2])
    schedule = scheduler.generate_daily_schedule()
    conflicts = scheduler.detect_conflicts(schedule)
    assert any("Duplicate task" in c and "Feed dog" in c for c in conflicts)


def test_conflict_detected_when_required_task_dropped():
    small = Task(description="Feed", duration_minutes=5,
                 frequency=Frequency.DAILY, priority=3, category="feeding")
    big_required = Task(description="Surgery follow-up", duration_minutes=90,
                        frequency=Frequency.DAILY, priority=5, category="medical",
                        required=True)
    scheduler, _ = _make_owner_with_tasks([small, big_required], available_minutes=10)
    schedule = scheduler.generate_daily_schedule()
    conflicts = scheduler.detect_conflicts(schedule)
    assert any("Required task" in c and "Surgery follow-up" in c for c in conflicts)


def test_no_conflicts_for_clean_schedule():
    t1 = Task(description="Morning walk", duration_minutes=20,
              frequency=Frequency.DAILY, priority=4, category="exercise")
    t2 = Task(description="Evening feed", duration_minutes=10,
              frequency=Frequency.DAILY, priority=3, category="feeding")
    scheduler, _ = _make_owner_with_tasks([t1, t2])
    schedule = scheduler.generate_daily_schedule()
    conflicts = scheduler.detect_conflicts(schedule)
    assert conflicts == []
