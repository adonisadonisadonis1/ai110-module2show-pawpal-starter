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
