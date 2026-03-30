from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime, timedelta

def main():
    print("🐾 Welcome to the PawPal+ CLI Testing Demo 🐾")
    print("-" * 50)

    # 1. Scaffold Core Objects
    owner = Owner("Jordan")
    milo = Pet("Milo", "Dog", 3)
    luna = Pet("Luna", "Cat", 2)
    
    owner.add_pet(milo)
    owner.add_pet(luna)

    # Create times for today
    now = datetime.now()
    time_1 = now.replace(hour=8, minute=0, second=0, microsecond=0)
    time_2 = now.replace(hour=8, minute=15, second=0, microsecond=0) # Intentional conflict!
    time_3 = now.replace(hour=18, minute=0, second=0, microsecond=0)

    # 2. Add Tasks
    # Notice we give the conflict a High priority, and the first task a Medium priority
    task1 = Task("Morning Walk", time_1, 30, priority="Medium", frequency="Daily")
    task2 = Task("Give Medication", time_2, 5, priority="High", frequency="Once")
    task3 = Task("Dinner", time_3, 10, priority="Low", frequency="Daily")

    milo.add_task(task1)
    milo.add_task(task2)
    luna.add_task(task3)

    # 3. Test Scheduler & Algorithms
    scheduler = Scheduler(owner)
    
    print("\n📅 TODAY'S SCHEDULE (Sorted by Priority -> Time):")
    upcoming = scheduler.get_upcoming_tasks()
    for pet_name, task in upcoming:
        time_str = task.due_time.strftime("%H:%M")
        print(f"[{task.priority.upper()}] {time_str} - {task.description} ({pet_name}) - {task.duration_mins} mins")

    print("\n🚨 CONFLICT CHECK:")
    conflicts = scheduler.check_conflicts()
    if conflicts:
        for c in conflicts:
            print(c)
    else:
        print("✅ No conflicts detected!")

    print("\n🔄 RECURRENCE CHECK:")
    print(f"Completing '{task1.description}' for {milo.name}...")
    scheduler.complete_and_reschedule(milo.name, task1.id)
    
    # Check if a new task was added for tomorrow
    new_tasks = [t for t in milo.tasks if t.description == "Morning Walk"]
    for t in new_tasks:
        print(f" - Found Task: {t.description} | Due: {t.due_time.strftime('%Y-%m-%d %H:%M')} | Completed: {t.is_completed}")

if __name__ == "__main__":
    main()