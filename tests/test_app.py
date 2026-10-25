"""Exercise the UI-to-model bridge through Streamlit reruns."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from pawpal_system import Owner, Pet, Task

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def click_button(app, label):
    for button in app.button:
        if button.label == label:
            button.click().run()
            return
    raise AssertionError(f"Button not found: {label}")


def test_pets_tasks_and_schedule_survive_reruns():
    app = AppTest.from_file(APP, default_timeout=15).run()
    owner = app.session_state["owner"]
    assert isinstance(owner, Owner)
    assert not owner.get_pets()
    app.text_input(key="pet_name").input("Mochi")
    click_button(app, "Add pet")
    app.text_input(key="pet_name").input("Luna")
    app.selectbox(key="species").select("cat")
    click_button(app, "Add pet")
    assert [pet.name for pet in owner.get_pets()] == ["Mochi", "Luna"]
    assert all(isinstance(pet, Pet) for pet in owner.get_pets())
    assert len(app.table[0].value) == 2

    app.selectbox(key="task_pet").select(1)
    app.text_input(key="task_title").input("Breakfast")
    click_button(app, "Add task")
    assert not owner.pets[0].tasks
    assert isinstance(owner.pets[1].tasks[0], Task)
    assert owner.pets[1].tasks[0].title == "Breakfast"
    click_button(app, "Generate schedule")
    assert app.table[-1].value.iloc[0]["Pet"] == "Luna"

    app.text_input(key="owner_name").input("Taylor")
    click_button(app, "Save owner")
    app.run()
    assert app.session_state["owner"] is owner
    assert owner.name == "Taylor"
    assert len(owner.pets) == 2
    assert len(owner.get_all_tasks()) == 1
    assert app.table[-1].value.iloc[0]["Task"] == "Breakfast"
    assert not app.exception


def test_blank_pet_and_task_are_rejected():
    app = AppTest.from_file(APP, default_timeout=15).run()
    click_button(app, "Add pet")
    assert not app.session_state["owner"].pets
    assert app.error[0].value == "Enter a pet name."
    app.text_input(key="pet_name").input("Mochi")
    click_button(app, "Add pet")
    click_button(app, "Add task")
    assert not app.session_state["owner"].get_all_tasks()
    assert app.error
    assert not app.exception


def test_smart_ui_sorts_filters_warns_and_completes_recurring_task():
    """The final UI exposes the same filtering, warnings, and recurrence as the CLI."""
    from datetime import date, time, timedelta

    today = date.today()
    owner = Owner("Jordan", 60)
    dog, cat = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    daily = Task("Walk", 20, "high", scheduled_time=time(8), due_date=today)
    dog.add_task(Task("Grooming", 10, "low", scheduled_time=time(9), frequency="once", due_date=today))
    dog.add_task(daily)
    cat.add_task(Task("Breakfast", 10, "high", scheduled_time=time(9), frequency="once", due_date=today))
    app = AppTest.from_file(APP, default_timeout=15)
    app.session_state["owner"] = owner
    app.run()
    assert list(app.table[1].value["Task"]) == ["Walk", "Grooming", "Breakfast"]
    assert len(app.warning) == 1
    assert "Mochi: Grooming" in app.warning[0].value
    assert "Luna: Breakfast" in app.warning[0].value

    app.selectbox(key="pet_filter").select("Mochi").run()
    app.selectbox(key="status_filter").select("Pending").run()
    assert list(app.table[1].value["Task"]) == ["Walk", "Grooming"]
    click_button(app, "Mark complete")
    assert daily.completed
    assert len(dog.tasks) == 3
    next_task = dog.tasks[-1]
    assert next_task.due_date == today + timedelta(days=1)
    assert not next_task.completed
    assert "Next occurrence" in app.success[0].value
    assert list(app.table[1].value["Task"]) == ["Grooming"]
    assert all("Walk" not in option for option in app.selectbox(key="completion_task").options)

    app.selectbox(key="status_filter").select("Completed").run()
    assert list(app.table[1].value["Task"]) == ["Walk"]
    app.selectbox(key="status_filter").select("Pending").run()
    app.date_input(key="plan_date").set_value(today + timedelta(days=1)).run()
    assert list(app.table[1].value["Task"]) == ["Walk"]
    assert not app.warning
    click_button(app, "Generate schedule")
    assert list(app.table[-1].value["Task"]) == ["Walk"]
    app.checkbox(key="all_dates").check().run()
    assert len(app.table[1].value) == 2
    assert not app.exception


def test_ui_task_due_date_is_saved():
    """A date entered in the task form reaches the backend Task object."""
    from datetime import date

    app = AppTest.from_file(APP, default_timeout=15).run()
    app.text_input(key="pet_name").input("Mochi")
    click_button(app, "Add pet")
    app.text_input(key="task_title").input("Vet visit")
    app.date_input(key="due_date").set_value(date(2030, 5, 10))
    app.selectbox(key="frequency").select("once")
    click_button(app, "Add task")
    task = app.session_state["owner"].get_all_tasks()[0]
    assert task.due_date == date(2030, 5, 10)
    assert task.frequency == "once"
    assert not app.exception
