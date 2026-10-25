"""Core pet-care models and a simple in-memory daily scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
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

    def update(self, title: str, duration_minutes: int,
               priority: Literal["low", "medium", "high"]) -> None:
        """Validate and update the description, duration, and priority together."""
        candidate = Task(title, duration_minutes, priority,
                         self.completed, self.scheduled_time, self.frequency)
        self.title = candidate.title
        self.duration_minutes = candidate.duration_minutes
        self.priority = candidate.priority

    def mark_complete(self) -> None:
        """Mark this care task complete."""
        self.completed = True


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

    def generate_daily_plan(self) -> List[Task]:
        """Select pending tasks chronologically while respecting the time budget."""
        tasks = self.owner.get_all_tasks()
        pending = sorted((task for task in tasks if not task.completed),
                         key=lambda task: task.scheduled_time)
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
                "Tasks are ordered by scheduled time; completed tasks and tasks "
                "that exceed the remaining budget are skipped.")
