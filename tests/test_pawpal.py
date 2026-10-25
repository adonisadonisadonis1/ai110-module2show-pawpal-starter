"""Core behavior and edge-case tests for the PawPal+ system."""

from datetime import date, time

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


@pytest.mark.parametrize("with_pet", [False, True], ids=["no-pets", "pet-with-no-tasks"])
def test_empty_schedule_is_safe(with_pet):
    """An owner with no care tasks has an empty plan, filters, and warnings."""
    owner = Owner("Jordan", 60)
    if with_pet:
        owner.add_pet(Pet("Mochi", "dog"))
    scheduler = Scheduler(owner)
    assert owner.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks(completed=False) == []
    assert scheduler.generate_daily_plan(date(2028, 2, 28)) == []
    assert scheduler.get_daily_plan() == []
    assert scheduler.detect_conflicts() == []
    assert "Planned 0 tasks totaling 0 of 60" in scheduler.explain_plan()


def test_sorting_and_daily_plan_handle_midnight_and_exclude_other_dates():
    """Time order spans the whole day without leaking adjacent dates into a plan."""
    day = date(2028, 2, 28)
    owner = Owner("Jordan", 60)
    pet = Pet("Luna", "cat")
    owner.add_pet(pet)
    late = Task("Late feeding", 10, "high", scheduled_time=time(23, 59), due_date=day)
    midnight = Task("Midnight medication", 10, "high", scheduled_time=time(0), due_date=day)
    yesterday = Task("Yesterday", 10, "high", due_date=date(2028, 2, 27))
    tomorrow = Task("Tomorrow", 10, "high", due_date=date(2028, 2, 29))
    for task in (late, tomorrow, midnight, yesterday):
        pet.add_task(task)
    scheduler = Scheduler(owner)
    assert [task.title for task in scheduler.sort_by_time()] == [
        "Yesterday", "Midnight medication", "Late feeding", "Tomorrow",
    ]
    assert scheduler.generate_daily_plan(day) == [midnight, late]
    assert pet.get_tasks() == [late, tomorrow, midnight, yesterday]


def test_daily_completion_creates_following_day_across_leap_day():
    """A daily occurrence advances through February 29 and stays with its pet."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    original = Task("Walk", 20, "high", scheduled_time=time(8), due_date=date(2028, 2, 28))
    pet.add_task(original)
    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan(date(2028, 2, 28))
    leap_day_task = scheduler.mark_task_complete(original, completed_on=date(2028, 2, 28))
    assert scheduler.get_daily_plan() == []
    assert original.completed is True
    assert leap_day_task is not original
    assert leap_day_task.due_date == date(2028, 2, 29)
    assert leap_day_task.completed is False
    assert leap_day_task.duration_minutes == 20
    assert leap_day_task.priority == "high"
    assert leap_day_task.scheduled_time == time(8)
    assert pet.tasks[-1] is leap_day_task
    march_task = scheduler.mark_task_complete(leap_day_task, completed_on=date(2028, 2, 29))
    assert march_task.due_date == date(2028, 3, 1)
    assert scheduler.generate_daily_plan(date(2028, 3, 1)) == [march_task]
    assert len(pet.get_tasks()) == 3


def test_duplicate_time_warnings_are_independent_and_resolve_on_completion():
    """Completing a task clears its clash without hiding an unrelated clash."""
    day = date(2028, 2, 28)
    owner = Owner("Jordan", 60)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    morning_walk = Task("Walk", 10, "high", scheduled_time=time(8), due_date=day)
    dog.add_task(morning_walk)
    cat.add_task(Task("Breakfast", 10, "high", scheduled_time=time(8), due_date=day))
    dog.add_task(Task("Grooming", 10, "low", scheduled_time=time(18), due_date=day))
    cat.add_task(Task("Dinner", 10, "high", scheduled_time=time(18), due_date=day))
    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(day)
    assert len(warnings) == 2
    assert any("08:00" in warning and "Mochi: Walk" in warning and "Luna: Breakfast" in warning
               for warning in warnings)
    assert any("18:00" in warning and "Mochi: Grooming" in warning and "Luna: Dinner" in warning
               for warning in warnings)
    scheduler.mark_task_complete(morning_walk, completed_on=day)
    remaining = scheduler.detect_conflicts(day)
    assert len(remaining) == 1
    assert "18:00" in remaining[0]
    assert scheduler.detect_conflicts(date(2028, 2, 29)) == []


@pytest.mark.parametrize("budget,expected_titles", [
    (0, []),
    (10, ["Breakfast"]),
    (30, ["Walk", "Breakfast"]),
])
def test_daily_budget_boundaries(budget, expected_titles):
    """Zero budgets select nothing, exact fits work, and oversized tasks are skipped."""
    day = date(2028, 2, 28)
    owner = Owner("Jordan", budget)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 20, "high", scheduled_time=time(8), due_date=day))
    pet.add_task(Task("Breakfast", 10, "high", scheduled_time=time(9), due_date=day))
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(day)
    assert [task.title for task in plan] == expected_titles
    assert sum(task.duration_minutes for task in plan) <= budget
    # A caller editing the returned list must not erase the stored plan.
    plan.clear()
    assert [task.title for task in scheduler.get_daily_plan()] == expected_titles


def test_lists_are_independent_and_getters_do_not_expose_collection_mutation():
    """Separate pets/owners do not share lists and getters return safe list copies."""
    owner, other_owner = Owner("Jordan", 60), Owner("Taylor", 60)
    pet, other_pet = Pet("Mochi", "dog"), Pet("Luna", "cat")
    task = Task("Walk", 20, "high", due_date=date(2028, 2, 28))
    owner.add_pet(pet)
    owner.add_pet(pet)
    pet.add_task(task)
    pet.add_task(task)
    assert len(owner.pets) == 1
    assert len(pet.tasks) == 1
    assert other_owner.pets == []
    assert other_pet.tasks == []
    owner.get_pets().clear()
    pet.get_tasks().clear()
    owner.get_all_tasks().clear()
    assert owner.pets == [pet]
    assert pet.tasks == [task]


@pytest.mark.parametrize("duration", [0, -1, 1.5, True])
def test_task_rejects_invalid_duration(duration):
    """Care durations must be positive whole minutes, excluding booleans."""
    with pytest.raises(ValueError, match="positive integer"):
        Task("Walk", duration, "high")


def test_partial_budget_skips_oversized_task_and_empty_day_clears_old_plan():
    """A task that no longer fits cannot block later work or leave a stale plan."""
    day = date(2028, 2, 28)
    owner = Owner("Jordan", 30)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    for title, duration, hour in [("Walk", 20, 8), ("Grooming", 11, 9), ("Feeding", 10, 10)]:
        pet.add_task(Task(title, duration, "high", scheduled_time=time(hour), due_date=day))
    scheduler = Scheduler(owner)
    assert [task.title for task in scheduler.generate_daily_plan(day)] == ["Walk", "Feeding"]
    assert [task.title for task in scheduler.generate_daily_plan(day)] == ["Walk", "Feeding"]
    assert scheduler.generate_daily_plan(date(2028, 2, 29)) == []
    assert scheduler.get_daily_plan() == []


def test_invalid_completion_date_leaves_task_and_plan_unchanged():
    """Rejected completion must not partially change the task or create recurrence."""
    day = date(2028, 2, 28)
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Walk", 20, "high", due_date=day)
    pet.add_task(task)
    scheduler = Scheduler(owner)
    scheduler.generate_daily_plan(day)
    with pytest.raises(ValueError, match="Completion date"):
        scheduler.mark_task_complete(task, completed_on="2028-02-28")
    assert task.completed is False
    assert len(pet.tasks) == 1
    assert pet.tasks[0] is task
    assert scheduler.get_daily_plan() == [task]
