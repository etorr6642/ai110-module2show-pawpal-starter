# Import classes from pawpal_system.py
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Frequency, Scheduler

# --- Setup ---
owner = Owner(name="Alice", email="alice@example.com", available_minutes_per_day=120)
pet1 = Pet(name="Buddy", breed="Golden Retriever", pet_type="dog")
pet2 = Pet(name="Whiskers", breed="Siamese", pet_type="cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

# Tasks added out of order (low priority / long duration first)
# so the sort by (-priority, duration_minutes) is clearly visible.

task_playtime = Task(
    description="Evening playtime",
    duration_minutes=25,
    frequency=Frequency.DAILY,
    priority=2,
    category="evening",
    required=False,
)
task_grooming = Task(
    description="Weekly grooming",
    duration_minutes=40,
    frequency=Frequency.WEEKLY,
    priority=3,
    category="morning",
    required=False,
    last_completed_date=date.today() - timedelta(days=8),
)
task_walk = Task(
    description="Morning walk",
    duration_minutes=30,
    frequency=Frequency.DAILY,
    priority=4,
    category="morning",
    required=True,
)
task_feeding_afternoon = Task(
    description="Afternoon feeding",
    duration_minutes=10,
    frequency=Frequency.DAILY,
    priority=5,
    category="afternoon",
    required=True,
)
task_medication = Task(
    description="Medication",
    duration_minutes=5,
    frequency=Frequency.DAILY,
    priority=5,
    category="morning",
    required=True,
)

# --- CONFLICT SCENARIO ---
# Two different tasks for Buddy both assigned to the "morning" slot.
# Medication (priority 5, 5 min) and Morning walk (priority 4, 30 min)
# already share the morning category — that will trigger the time slot conflict.
# Adding a third morning task makes the collision unmistakable.
task_training = Task(
    description="Training session",
    duration_minutes=20,
    frequency=Frequency.DAILY,
    priority=4,
    category="morning",   # same slot as Medication and Morning walk
    required=True,
)

task_litter = Task(
    description="Clean litter box",
    duration_minutes=15,
    frequency=Frequency.DAILY,
    priority=4,
    category="afternoon",
    required=True,
)

# Buddy gets three morning tasks — conflict expected
pet1.add_task(task_playtime)
pet1.add_task(task_grooming)
pet1.add_task(task_walk)           # morning
pet1.add_task(task_medication)     # morning — same slot as walk
pet1.add_task(task_training)       # morning — same slot as walk + medication
pet1.add_task(task_feeding_afternoon)

pet2.add_task(task_playtime)       # shared object — deduplication applies
pet2.add_task(task_litter)
pet2.add_task(task_feeding_afternoon)  # shared object — deduplication applies

# Mark grooming complete so it is excluded from today's schedule
task_grooming.mark_completed()

# --- Generate schedule ---
scheduler = Scheduler(owner)
schedule = scheduler.generate_daily_schedule()

print("=" * 55)
print("FULL SCHEDULE (sorted by priority desc, duration asc)")
print("=" * 55)
print(scheduler.get_schedule_summary(schedule))

# --- Filter by pet ---
print()
print("=" * 55)
print("BUDDY'S TASKS (filter_by_pet)")
print("=" * 55)
buddy_tasks = scheduler.filter_by_pet(schedule, pet1.pet_id)
if buddy_tasks:
    for pet, task in buddy_tasks:
        print(f"  • [{task.category}] {task.description} — {task.duration_minutes} min, priority {task.priority}")
else:
    print("  No tasks scheduled for Buddy.")

print()
print("=" * 55)
print("WHISKERS'S TASKS (filter_by_pet)")
print("=" * 55)
whiskers_tasks = scheduler.filter_by_pet(schedule, pet2.pet_id)
if whiskers_tasks:
    for pet, task in whiskers_tasks:
        print(f"  • [{task.category}] {task.description} — {task.duration_minutes} min, priority {task.priority}")
else:
    print("  No tasks scheduled for Whiskers.")

# --- Filter by status ---
print()
print("=" * 55)
print("COMPLETED TASKS (filter_by_status)")
print("=" * 55)
completed = scheduler.filter_by_status(completed=True)
if completed:
    for pet, task in completed:
        print(f"  • [{pet.name}] {task.description} — last done {task.last_completed_date}")
else:
    print("  No completed tasks.")

print()
print("=" * 55)
print("INCOMPLETE TASKS (filter_by_status)")
print("=" * 55)
incomplete = scheduler.filter_by_status(completed=False)
if incomplete:
    for pet, task in incomplete:
        print(f"  • [{pet.name}] {task.description} — priority {task.priority}")
else:
    print("  All tasks complete!")

# --- Recurring task check ---
print()
print("=" * 55)
print("RECURRING TASK CHECK (is_due_today)")
print("=" * 55)
bath = Task(
    description="Bath",
    duration_minutes=30,
    frequency=Frequency.WEEKLY,
    priority=3,
    category="morning",
    required=False,
    last_completed_date=date.today() - timedelta(days=3),
)
nail_trim = Task(
    description="Nail trim",
    duration_minutes=20,
    frequency=Frequency.WEEKLY,
    priority=3,
    category="morning",
    required=False,
    last_completed_date=date.today() - timedelta(days=10),
)
print(f"  'Bath' (last done 3 days ago, weekly):    due today? {bath.is_due_today()}")
print(f"  'Nail trim' (last done 10 days ago, weekly): due today? {nail_trim.is_due_today()}")

# --- Conflict detection (standalone, so warnings print separately from summary) ---
print()
print("=" * 55)
print("CONFLICT DETECTION (detect_conflicts)")
print("=" * 55)
conflicts = scheduler.detect_conflicts(schedule)
if conflicts:
    for conflict in conflicts:
        print(f"  ! {conflict}")
else:
    print("  No conflicts detected.")
