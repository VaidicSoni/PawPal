import json
import uuid
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

@dataclass
class Task:
    """Represents a single care activity for a pet."""
    description: str
    due_time: datetime
    duration_mins: int
    priority: str  # "High", "Medium", "Low"
    frequency: str = "Once"  # "Once", "Daily", "Weekly"
    is_completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> Optional['Task']:
        """Marks the task as complete and returns a new task instance if it is recurring."""
        self.is_completed = True
        
        # Stretch Goal: Automate Recurring Tasks using timedelta
        if self.frequency == "Daily":
            new_time = self.due_time + timedelta(days=1)
            return Task(self.description, new_time, self.duration_mins, self.priority, self.frequency)
        elif self.frequency == "Weekly":
            new_time = self.due_time + timedelta(weeks=1)
            return Task(self.description, new_time, self.duration_mins, self.priority, self.frequency)
        return None

@dataclass
class Pet:
    """Stores pet details and a list of their specific tasks."""
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Adds a task to the pet's profile."""
        self.tasks.append(task)

class Owner:
    """Manages multiple pets and acts as the central data store."""
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Registers a new pet to the owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        """Returns a list of tuples containing (pet_name, task) for all pets."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))
        return all_tasks

    # Stretch Goal 2: Data Persistence via JSON
    def save_to_json(self, filename="pawpal_data.json"):
        """Serializes the Owner, Pets, and Tasks to a JSON file."""
        data = {"name": self.name, "pets": []}
        for p in self.pets:
            pet_data = {"name": p.name, "species": p.species, "age": p.age, "tasks": []}
            for t in p.tasks:
                task_dict = asdict(t)
                # datetime isn't naturally JSON serializable, so we convert it to an ISO string
                task_dict['due_time'] = t.due_time.isoformat()
                pet_data["tasks"].append(task_dict)
            data["pets"].append(pet_data)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_json(cls, filename="pawpal_data.json") -> Optional['Owner']:
        """Deserializes JSON data back into an Owner object with all Pets and Tasks."""
        if not os.path.exists(filename):
            return None
            
        with open(filename, 'r') as f:
            data = json.load(f)
            
        owner = cls(data["name"])
        for p_data in data.get("pets", []):
            pet = Pet(p_data["name"], p_data["species"], p_data["age"])
            for t_data in p_data.get("tasks", []):
                # Convert ISO string back to datetime object
                t_data['due_time'] = datetime.fromisoformat(t_data['due_time'])
                pet.tasks.append(Task(**t_data))
            owner.add_pet(pet)
        return owner

class Scheduler:
    """The 'Brain' of the system that retrieves, organizes, and manages tasks."""
    def __init__(self, owner: Owner):
        self.owner = owner
        # Map for Stretch Goal 3: Priority-Based Scheduling
        self.priority_map = {"High": 1, "Medium": 2, "Low": 3}

    def get_upcoming_tasks(self, include_completed=False) -> List[Tuple[str, Task]]:
        """
        Retrieves tasks and sorts them.
        Stretch Goal 3: Sorts by Priority level first, then chronologically by time.
        """
        tasks = self.owner.get_all_tasks()
        if not include_completed:
            tasks = [t for t in tasks if not t[1].is_completed]
        
        # Sort using a lambda key: (Priority Integer, DateTime)
        tasks.sort(key=lambda x: (self.priority_map.get(x[1].priority, 3), x[1].due_time))
        return tasks

    def check_conflicts(self) -> List[str]:
        """Detects if any incomplete tasks overlap in time, regardless of the pet."""
        tasks = self.get_upcoming_tasks(include_completed=False)
        conflicts = []
        
        # For conflict checking, we must sort purely by time (ignore priority)
        tasks_by_time = sorted(tasks, key=lambda x: x[1].due_time)
        
        for i in range(len(tasks_by_time) - 1):
            pet1, t1 = tasks_by_time[i]
            pet2, t2 = tasks_by_time[i+1]
            
            t1_end_time = t1.due_time + timedelta(minutes=t1.duration_mins)
            
            if t2.due_time < t1_end_time:
                conflicts.append(f"⚠️ Conflict: {pet1}'s '{t1.description}' (Ends: {t1_end_time.strftime('%H:%M')}) overlaps with {pet2}'s '{t2.description}' (Starts: {t2.due_time.strftime('%H:%M')}).")
                
        return conflicts

    # Stretch Goal 1: Advanced Algorithmic Capability (Next available slot)
    def find_next_available_slot(self, start_time: datetime, duration_mins: int) -> datetime:
        """Finds the first available block of time for a new task to avoid conflicts."""
        tasks = sorted([t for t in self.owner.get_all_tasks() if not t[1].is_completed], key=lambda x: x[1].due_time)
        current_time = start_time
        
        for pet, task in tasks:
            task_start = task.due_time
            task_end = task_start + timedelta(minutes=task.duration_mins)
            
            # If our proposed block fits entirely before the next scheduled task, we found a slot!
            if current_time + timedelta(minutes=duration_mins) <= task_start:
                return current_time
            
            # Otherwise, jump our 'current_time' to the end of this blocking task
            if current_time < task_end:
                current_time = task_end
                
        return current_time

    def complete_and_reschedule(self, pet_name: str, task_id: str):
        """Marks a task complete and handles adding the recurring instance if applicable."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.id == task_id and not task.is_completed:
                        new_recurring_task = task.mark_complete()
                        if new_recurring_task:
                            pet.add_task(new_recurring_task)
                        return True
        return False