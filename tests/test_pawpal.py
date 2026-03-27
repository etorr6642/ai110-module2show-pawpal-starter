from pawpal_system import Task, Pet, Frequency


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
