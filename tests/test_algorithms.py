"""Verify Phase 4 algorithms with deterministic due and completion dates."""

from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 10, 25)


def make_scheduler():
    owner = Owner("Jordan", 60)
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Luna", "cat"))
    return Scheduler(owner)


def test_sorting_is_stable_chronological_and_does_not_mutate():
    scheduler = make_scheduler()
    late = Task("Late", 10, "low", scheduled_time=time(18), due_date=TODAY)
    early = Task("Early", 10, "high", scheduled_time=time(8), due_date=TODAY)
    tied = Task("Tie", 10, "high", scheduled_time=time(8), due_date=TODAY)
    tomorrow = Task("Tomorrow", 10, "high", scheduled_time=time(7), due_date=TODAY + timedelta(days=1))
    original = [tomorrow, late, early, tied]
    assert scheduler.sort_by_time(original) == [early, tied, late, tomorrow]
    assert original == [tomorrow, late, early, tied]
    assert scheduler.sort_by_time([]) == []


def test_filters_combine_pet_status_and_date():
    scheduler = make_scheduler()
    pending = Task("Feeding", 10, "high", due_date=TODAY)
    done = Task("Feeding", 10, "high", completed=True, due_date=TODAY)
    future = Task("Future", 10, "high", due_date=TODAY + timedelta(days=1))
    scheduler.owner.pets[0].add_task(pending)
    scheduler.owner.pets[1].add_task(done)
    scheduler.owner.pets[1].add_task(future)
    assert scheduler.filter_tasks(pet_name=" moCHI ", completed=False, on_date=TODAY) == [pending]
    assert scheduler.filter_tasks(completed=True) == [done]
    assert scheduler.filter_tasks(pet_name="missing") == []
    assert len(scheduler.filter_tasks()) == 3


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7), ("once", None)])
def test_completion_creates_and_attaches_only_one_next_occurrence(frequency, days):
    scheduler = make_scheduler()
    pet = scheduler.owner.pets[1]
    task = Task("Care", 10, "high", scheduled_time=time(8, 30),
                frequency=frequency, due_date=TODAY)
    pet.add_task(task)
    following = scheduler.mark_task_complete(task, completed_on=TODAY)
    assert task.completed
    if days is None:
        assert following is None
        assert len(pet.tasks) == 1
    else:
        assert following is not task
        assert following.due_date == TODAY + timedelta(days=days)
        assert not following.completed
        assert following.title == task.title
        assert following.scheduled_time == task.scheduled_time
        assert following.frequency == task.frequency
        assert pet.tasks[-1] is following
        assert following not in scheduler.generate_daily_plan(TODAY)
        assert scheduler.generate_daily_plan(following.due_date) == [following]
    count = len(pet.tasks)
    assert scheduler.mark_task_complete(task, completed_on=TODAY) is None
    assert len(pet.tasks) == count
    assert scheduler.owner.pets[0].tasks == []


def test_recurrence_handles_late_completion_and_month_rollover():
    task = Task("Walk", 10, "high", due_date=date(2026, 12, 30))
    following = task.mark_complete(completed_on=date(2026, 12, 31))
    assert following.due_date == date(2027, 1, 1)


def test_early_completion_advances_from_due_date():
    task = Task("Walk", 10, "high", due_date=TODAY + timedelta(days=3))
    assert task.mark_complete(completed_on=TODAY).due_date == TODAY + timedelta(days=4)


def test_unknown_task_cannot_be_completed_by_scheduler():
    scheduler = make_scheduler()
    task = Task("Unknown", 10, "high", due_date=TODAY)
    with pytest.raises(ValueError, match="does not belong"):
        scheduler.mark_task_complete(task, TODAY)
    assert not task.completed


def test_conflicts_cover_same_and_different_pets_and_exclude_other_dates_and_completed():
    scheduler = make_scheduler()
    for pet, title in [(scheduler.owner.pets[0], "Walk"),
                       (scheduler.owner.pets[0], "Medication"),
                       (scheduler.owner.pets[1], "Breakfast")]:
        pet.add_task(Task(title, 10, "high", due_date=TODAY))
    scheduler.owner.pets[1].add_task(Task("Done", 10, "high", completed=True, due_date=TODAY))
    scheduler.owner.pets[1].add_task(Task("Tomorrow", 10, "high", due_date=TODAY + timedelta(days=1)))
    warnings = scheduler.detect_conflicts(TODAY)
    assert len(warnings) == 1
    assert all(label in warnings[0] for label in ("Mochi: Walk", "Mochi: Medication", "Luna: Breakfast", "09:00"))
    assert "Done" not in warnings[0] and "Tomorrow" not in warnings[0]
    assert scheduler.detect_conflicts(TODAY + timedelta(days=1)) == []
    assert len(scheduler.generate_daily_plan(TODAY)) == 3


def test_different_start_times_do_not_warn_even_when_durations_overlap():
    scheduler = make_scheduler()
    pet = scheduler.owner.pets[0]
    pet.add_task(Task("Walk", 30, "high", scheduled_time=time(8), due_date=TODAY))
    pet.add_task(Task("Feeding", 10, "high", scheduled_time=time(8, 15), due_date=TODAY))
    assert scheduler.detect_conflicts(TODAY) == []


def test_shared_task_instance_has_correct_conflict_labels_and_cannot_recur_ambiguously():
    scheduler = make_scheduler()
    shared = Task("Shared", 10, "high", due_date=TODAY)
    for pet in scheduler.owner.pets:
        pet.add_task(shared)
    warning = scheduler.detect_conflicts(TODAY)[0]
    assert "Mochi: Shared" in warning and "Luna: Shared" in warning
    with pytest.raises(ValueError, match="only one pet"):
        scheduler.mark_task_complete(shared, TODAY)
    assert not shared.completed
    assert len(scheduler.owner.get_all_tasks()) == 2


def test_same_pet_name_filter_matches_both_but_completion_uses_identity():
    scheduler = make_scheduler()
    scheduler.owner.pets[1].name = "Mochi"
    first = Task("Care", 10, "high", due_date=TODAY)
    second = Task("Care", 10, "high", due_date=TODAY)
    scheduler.owner.pets[0].add_task(first)
    scheduler.owner.pets[1].add_task(second)
    assert len(scheduler.filter_tasks(pet_name="mochi")) == 2
    following = scheduler.mark_task_complete(second, TODAY)
    assert not first.completed
    assert scheduler.owner.pets[1].tasks[-1] is following
    assert len(scheduler.owner.pets[0].tasks) == 1
