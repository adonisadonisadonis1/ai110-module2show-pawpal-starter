"""Run the Phase 2 CLI demo with two pets and three care tasks."""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Create sample pets and print their combined daily care plan."""
    owner = Owner(name="Jordan", available_minutes=60)
    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Luna", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Morning walk", 20, "high", scheduled_time=time(8, 0)))
    dog.add_task(Task("Evening grooming", 15, "low", scheduled_time=time(18, 0)))
    cat.add_task(Task("Breakfast", 10, "high", scheduled_time=time(8, 30)))

    scheduler = Scheduler(owner)
    print("Today's Schedule")
    print(f"Owner: {owner.name} | Pets: {', '.join(pet.name for pet in owner.get_pets())}")
    for task in scheduler.generate_daily_plan():
        pet = scheduler.get_pet_for_task(task)
        print(f"{task.scheduled_time:%H:%M} | {pet.name if pet else 'Unknown pet'} | "
              f"{task.title} | {task.duration_minutes} min | "
              f"{task.priority} priority | {task.frequency}")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
