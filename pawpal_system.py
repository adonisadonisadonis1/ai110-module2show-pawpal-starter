"""Core pet-care models and a simple in-memory daily scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from typing import List, Literal, Optional


@dataclass
class Task:
    """A care activity with a description, duration, time, and frequency."""

    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    completed: bool = False
    scheduled_time: time = time(9, 0)
    frequency: str = "daily"
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Reject missing descriptions, invalid durations, priorities, or times."""
        if not self.title.strip() or not self.frequency.strip():
            raise ValueError("Task title and frequency must not be blank.")
        if isinstance(self.duration_minutes, bool) or not isinstance(self.duration_minutes, int) or self.duration_minutes <= 0:
            raise ValueError("Task duration must be a positive integer in minutes.")
        if self.priority not in ("low", "medium", "high"):
            raise ValueError("Task priority must be low, medium, or high.")
        if not isinstance(self.scheduled_time, time):
            raise ValueError("Task scheduled_time must be a datetime.time value.")
        if self.frequency not in ("daily", "weekly", "once"):
            raise ValueError("Task frequency must be daily, weekly, or once.")
        if type(self.due_date) is not date:
            raise ValueError("Task due_date must be a datetime.date value.")

    def update(self, title: str, duration_minutes: int,
               priority: Literal["low", "medium", "high"]) -> None:
        """Validate and update the description, duration, and priority together."""
        candidate = Task(title, duration_minutes, priority,
                         self.completed, self.scheduled_time, self.frequency, self.due_date)
        self.title = candidate.title
        self.duration_minutes = candidate.duration_minutes
        self.priority = candidate.priority

    def mark_complete(self, completed_on: Optional[date] = None) -> Optional[Task]:
        """Complete once and return the next recurring occurrence, if applicable."""
        if self.completed:
            return None
        completed_on = completed_on if completed_on is not None else date.today()
        if type(completed_on) is not date:
            raise ValueError("Completion date must be a datetime.date value.")
        next_task = None
        days = {"daily": 1, "weekly": 7}.get(self.frequency)
        if days is not None:
            next_task = replace(
                self, completed=False,
                due_date=max(self.due_date, completed_on) + timedelta(days=days),
            )
        self.completed = True
        return next_task


@dataclass
class Pet:
    """A pet with its own collection of care tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task without duplicating the same task instance."""
        if not any(existing is task for existing in self.tasks):
            self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return a copy of the task list while preserving its task objects."""
        return list(self.tasks)


@dataclass
class Owner:
    """Owner details, daily time budget, preferences, and owned pets."""

    name: str
    available_minutes: int
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Require a nonnegative integer daily time budget."""
        if isinstance(self.available_minutes, bool) or not isinstance(self.available_minutes, int) or self.available_minutes < 0:
            raise ValueError("Available minutes must be a nonnegative integer.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet without duplicating the same pet instance."""
        if not any(existing is pet for existing in self.pets):
            self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> List[Task]:
        """Collect tasks from every pet belonging to this owner."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
    """Organize pending tasks across all of one owner's pets."""

    owner: Owner
    daily_plan: List[Task] = field(default_factory=list)

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks in stable date/time order without changing the input list."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda task: (task.due_date, task.scheduled_time))

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None,
                     on_date: Optional[date] = None) -> List[Task]:
        """Filter all pets' tasks by optional pet name, status, and due date."""
        tasks = self.owner.get_all_tasks()
        pet_task_ids = None
        if pet_name is not None:
            pet_task_ids = {
                id(task) for pet in self.owner.get_pets()
                if pet.name.casefold() == pet_name.strip().casefold()
                for task in pet.get_tasks()
            }
        return [task for task in tasks
                if (pet_task_ids is None or id(task) in pet_task_ids)
                and (completed is None or task.completed == completed)
                and (on_date is None or task.due_date == on_date)]

    def mark_task_complete(self, task: Task,
                           completed_on: Optional[date] = None) -> Optional[Task]:
        """Complete an owned task and automatically attach its next occurrence."""
        owning_pets = [pet for pet in self.owner.get_pets()
                       if any(existing is task for existing in pet.get_tasks())]
        if not owning_pets:
            raise ValueError("Task does not belong to this owner's pets.")
        if len(owning_pets) > 1:
            raise ValueError("A task instance must belong to only one pet.")
        pet = owning_pets[0]
        next_task = task.mark_complete(completed_on)
        if next_task is not None:
            pet.add_task(next_task)
        self.daily_plan = []
        return next_task

    def detect_conflicts(self, on_date: Optional[date] = None) -> List[str]:
        """Warn about pending tasks sharing an exact date/time across any pets."""
        slots = {}
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.completed or (on_date is not None and task.due_date != on_date):
                    continue
                slot = (task.due_date, task.scheduled_time)
                slots.setdefault(slot, []).append(f"{pet.name}: {task.title}")
        warnings = []
        for (due_date, scheduled_time), labels in slots.items():
            if len(labels) > 1:
                warnings.append(
                    f"Warning: {due_date.isoformat()} {scheduled_time:%H:%M} conflict: "
                    + "; ".join(labels)
                )
        return warnings

    def generate_daily_plan(self, on_date: Optional[date] = None) -> List[Task]:
        """Select pending tasks due on a day in time order within the time budget."""
        on_date = on_date if on_date is not None else date.today()
        pending = self.sort_by_time(self.filter_tasks(completed=False, on_date=on_date))
        remaining = self.owner.available_minutes
        self.daily_plan = []
        for task in pending:
            if task.duration_minutes <= remaining:
                self.daily_plan.append(task)
                remaining -= task.duration_minutes
        return self.get_daily_plan()

    def get_daily_plan(self) -> List[Task]:
        """Return a copy of the most recently generated daily plan."""
        return list(self.daily_plan)

    def get_pet_for_task(self, task: Task) -> Optional[Pet]:
        """Find a task's pet by object identity rather than matching task values."""
        for pet in self.owner.get_pets():
            if any(existing is task for existing in pet.get_tasks()):
                return pet
        return None

    def explain_plan(self) -> str:
        """Summarize the current plan and the simple selection rules."""
        minutes = sum(task.duration_minutes for task in self.daily_plan)
        return (f"Planned {len(self.daily_plan)} tasks totaling {minutes} of "
                f"{self.owner.available_minutes} available minutes. "
                "Only tasks due on the selected day are considered. "
                "Tasks are ordered by scheduled time; completed tasks and tasks "
                "that exceed the remaining budget are skipped.")
