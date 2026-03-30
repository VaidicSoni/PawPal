import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

def test_task_completion():
    """Verify that calling mark_complete() changes status."""
    now = datetime.now()
    task = Task("Walk", now, 30, "Low", "Once")
    assert not task.is_completed
    
    result = task.mark_complete()
    assert task.is_completed
    assert result is None # 'Once' frequency shouldn't return a new task

def test_task_addition():
    """Verify that adding a task to a Pet increases task count."""
    milo = Pet("Milo", "Dog", 3)
    assert len(milo.tasks) == 0
    
    milo.add_task(Task("Feed", datetime.now(), 5, "High"))
    assert len(milo.tasks) == 1

def test_sorting_correctness():
    """Verify tasks are returned sorted by Priority, then chronologically."""
    owner = Owner("Test Owner")
    pet = Pet("Test Pet", "Cat", 2)
    owner.add_pet(pet)
    
    time1 = datetime(2025, 1, 1, 10, 0)
    time2 = datetime(2025, 1, 1, 12, 0)
    
    # Task 2 is later, but High priority. It should come FIRST.
    task1 = Task("Low Priority Early", time1, 10, "Low")
    task2 = Task("High Priority Later", time2, 10, "High")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler(owner)
    upcoming = scheduler.get_upcoming_tasks()
    
    assert upcoming[0][1].description == "High Priority Later"
    assert upcoming[1][1].description == "Low Priority Early"

def test_recurrence_logic():
    """Confirm that marking a daily task complete creates a new task for tomorrow."""
    time1 = datetime(2025, 1, 1, 10, 0)
    task = Task("Daily Meds", time1, 5, "High", "Daily")
    
    new_task = task.mark_complete()
    
    assert new_task is not None
    assert new_task.is_completed is False
    # Verify exact 1 day timedelta
    assert new_task.due_time == datetime(2025, 1, 2, 10, 0)

def test_conflict_detection():
    """Verify that the Scheduler flags duplicate/overlapping times."""
    owner = Owner("Test Owner")
    pet = Pet("Test Pet", "Cat", 2)
    owner.add_pet(pet)
    
    time1 = datetime(2025, 1, 1, 10, 0)
    
    # Task 1: 10:00 to 10:30
    task1 = Task("Walk", time1, 30, "Medium")
    # Task 2: 10:15 to 10:45 (Overlaps!)
    task2 = Task("Groom", time1 + timedelta(minutes=15), 30, "Low")
    
    pet.add_task(task1)
    pet.add_task(task2)
    
    scheduler = Scheduler(owner)
    conflicts = scheduler.check_conflicts()
    
    assert len(conflicts) == 1
    assert "overlaps" in conflicts[0]