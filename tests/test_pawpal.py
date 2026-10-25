"""Quick Phase 2 checks for task management and multi-pet scheduling."""

from datetime import time

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    task = Task("Walk", 20, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    pet = Pet("Mochi", "dog")
    task = Task("Walk", 20, "high")
    initial_count = len(pet.get_tasks())
    pet.add_task(task)
    assert len(pet.get_tasks()) == initial_count + 1
    assert pet.get_tasks()[-1] is task


def test_scheduler_uses_owner_aggregation_for_multiple_pets(monkeypatch):
    owner = Owner("Jordan", 60)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    late = Task("Walk", 20, "high", scheduled_time=time(10, 0))
    early = Task("Breakfast", 10, "high", scheduled_time=time(8, 0))
    dog.add_task(late)
    cat.add_task(early)
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert owner.get_all_tasks() == [late, early]
    original = owner.get_all_tasks
    calls = []

    def collect():
        calls.append(True)
        return original()

    monkeypatch.setattr(owner, "get_all_tasks", collect)
    scheduler = Scheduler(owner)
    assert scheduler.generate_daily_plan() == [early, late]
    assert calls == [True]
    assert scheduler.get_pet_for_task(early) is cat


def test_scheduler_skips_completed_and_over_budget_tasks():
    owner = Owner("Jordan", 15)
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    pet.add_task(Task("Done", 5, "high", completed=True, scheduled_time=time(7)))
    pet.add_task(Task("Too long", 20, "high", scheduled_time=time(8)))
    fitting = Task("Feeding", 10, "high", scheduled_time=time(9))
    pet.add_task(fitting)
    scheduler = Scheduler(owner)
    assert scheduler.generate_daily_plan() == [fitting]
    fitting.mark_complete()
    assert scheduler.generate_daily_plan() == []


def test_invalid_update_preserves_existing_task():
    task = Task("Walk", 20, "high")
    with pytest.raises(ValueError):
        task.update("Feeding", -1, "medium")
    assert (task.title, task.duration_minutes, task.priority) == ("Walk", 20, "high")
