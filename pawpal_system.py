"""Phase 1 blueprint for PawPal+: attributes and empty method stubs only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional


@dataclass
class Task:
    """One care task for one pet; priority is low, medium, or high."""

    title: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    completed: bool = False

    def update(self, title: str, duration_minutes: int,
               priority: Literal["low", "medium", "high"]) -> None:
        """Update the task details (implementation deferred)."""
        pass

    def mark_complete(self) -> None:
        """Mark this care task complete (implementation deferred)."""
        pass


@dataclass
class Pet:
    """A pet and its care tasks; its owner holds the pet reference."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Associate a care task with this pet (implementation deferred)."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return this pet's care tasks (implementation deferred)."""
        pass


@dataclass
class Owner:
    """Owner details, daily time budget, preferences, and owned pets."""

    name: str
    available_minutes: int
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Associate a pet with this owner (implementation deferred)."""
        pass

    def get_pets(self) -> List[Pet]:
        """Return this owner's pets (implementation deferred)."""
        pass


@dataclass
class Scheduler:
    """Plan one owner's day across their pets using the same Task objects."""

    owner: Owner
    daily_plan: List[Task] = field(default_factory=list)

    def generate_daily_plan(self) -> List[Task]:
        """Choose and order pending tasks within the time budget (deferred)."""
        pass

    def get_daily_plan(self) -> List[Task]:
        """Return the most recently generated daily plan (deferred)."""
        pass

    def get_pet_for_task(self, task: Task) -> Optional[Pet]:
        """Find a task's pet through the owner's pets (deferred)."""
        pass

    def explain_plan(self) -> str:
        """Explain selection using time, priorities, and preferences (deferred)."""
        pass
