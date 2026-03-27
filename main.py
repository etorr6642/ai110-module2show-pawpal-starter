# Import classes from pawpal_system.py
from pawpal_system import Owner, Pet, Task, Frequency, Scheduler

# Create an Owner and at least two Pets
owner = Owner(name="Alice", email="alice@example.com", available_minutes_per_day=120)
pet1 = Pet(name="Buddy", breed="Golden Retriever", pet_type="dog")
pet2 = Pet(name="Whiskers", breed="Siamese", pet_type="cat")
owner.add_pet(pet1)
owner.add_pet(pet2)

# Add at least three Tasks with different times (morning, afternoon, evening)
task1 = Task(
    description="Morning walk",
    duration_minutes=30,
    frequency=Frequency.DAILY,
    priority=5,
    category="morning",
    required=True,
)
task2 = Task(
    description="Afternoon feeding",
    duration_minutes=10,
    frequency=Frequency.DAILY,
    priority=4,
    category="afternoon",
    required=True,
)
task3 = Task(
    description="Evening playtime",
    duration_minutes=20,
    frequency=Frequency.DAILY,
    priority=3,
    category="evening",
    required=False,
)
task4 = Task(
    description="Morning feeding",
    duration_minutes=10,
    frequency=Frequency.DAILY,
    priority=5,
    category="morning",
    required=True,
)

pet1.add_task(task1)
pet1.add_task(task2)
pet1.add_task(task3)

pet2.add_task(task4)
pet2.add_task(task2)
pet2.add_task(task3)

# Print Today's Schedule using Scheduler
scheduler = Scheduler(owner)
schedule = scheduler.generate_daily_schedule()

print("=== Today's Schedule ===")
print(scheduler.get_schedule_summary(schedule))
