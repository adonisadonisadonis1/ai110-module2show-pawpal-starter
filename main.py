"""Demonstrate Phase 4 sorting, filtering, recurrence, and conflict warnings."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(label, tasks, scheduler):
    """Print readable task rows including each task's pet and due date."""
    print(f"\n{label}")
    if not tasks:
        print("(none)")
    for task in tasks:
        pet = scheduler.get_pet_for_task(task)
        status = "complete" if task.completed else "pending"
        print(f"{task.due_date} {task.scheduled_time:%H:%M} | {pet.name} | "
              f"{task.title} | {task.duration_minutes} min | {task.frequency} | {status}")


def main() -> None:
    """Exercise each algorithm using two pets and deliberately unordered tasks."""
    today = date.today()
    owner = Owner(name="Jordan", available_minutes=60)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    grooming = Task("Evening grooming", 15, "low", scheduled_time=time(18),
                    frequency="weekly", due_date=today)
    walk = Task("Morning walk", 20, "high", scheduled_time=time(8), due_date=today)
    breakfast = Task("Breakfast", 10, "high", scheduled_time=time(8), due_date=today)
    enrichment = Task("Enrichment", 5, "medium", scheduled_time=time(12),
                      frequency="once", due_date=today)
    dog.add_task(grooming)
    dog.add_task(walk)
    cat.add_task(enrichment)
    cat.add_task(breakfast)
    scheduler = Scheduler(owner)

    print_tasks("Tasks in insertion order", owner.get_all_tasks(), scheduler)
    print_tasks("Sorted by date and time", scheduler.sort_by_time(), scheduler)
    print_tasks("Luna's pending tasks", scheduler.sort_by_time(
        scheduler.filter_tasks(pet_name="Luna", completed=False)), scheduler)
    print_tasks("Today's Schedule", scheduler.generate_daily_plan(today), scheduler)
    print(scheduler.explain_plan())
    print("\nConflict checks")
    for warning in scheduler.detect_conflicts(today):
        print(warning)

    print("\nComplete daily walk and weekly grooming")
    next_walk = scheduler.mark_task_complete(walk, completed_on=today)
    next_grooming = scheduler.mark_task_complete(grooming, completed_on=today)
    print(f"Next daily walk: {next_walk.due_date} {next_walk.scheduled_time:%H:%M}")
    print(f"Next weekly grooming: {next_grooming.due_date} {next_grooming.scheduled_time:%H:%M}")
    print_tasks("Completed tasks", scheduler.filter_tasks(completed=True), scheduler)
    print_tasks("Today's remaining schedule", scheduler.generate_daily_plan(today), scheduler)
    print("Remaining conflicts:", scheduler.detect_conflicts(today) or "none")


if __name__ == "__main__":
    main()
