"""Streamlit interface backed by the session's PawPal owner and pets."""

from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.write("Add your pets and care tasks, then build a daily plan.")
st.caption("Data stays available during this session's reruns; a new session starts empty.")

# Create the object once; all forms below mutate this same owner.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)
if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False
owner = st.session_state.owner

st.subheader("Owner")
with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value=owner.name, key="owner_name")
    available_minutes = st.number_input(
        "Available minutes today", min_value=0, value=owner.available_minutes,
        step=1, key="available_minutes",
    )
    if st.form_submit_button("Save owner"):
        if owner_name.strip():
            owner.name = owner_name.strip()
            owner.available_minutes = int(available_minutes)
            st.success("Owner details saved.")
        else:
            st.error("Enter an owner name.")

st.subheader("Pets")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", key="pet_name")
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.error("Enter a pet name.")

# Render after the form so a submitted pet appears in the same rerun.
pets = owner.get_pets()
if pets:
    st.table([{"Pet": pet.name, "Species": pet.species} for pet in pets])
else:
    st.info("Add a pet to start scheduling care tasks.")

st.subheader("Tasks")
if pets:
    with st.form("task_form", clear_on_submit=True):
        pet_index = st.selectbox(
            "Pet", options=range(len(pets)), key="task_pet",
            format_func=lambda index: f"{index + 1}. {pets[index].name} ({pets[index].species})",
        )
        task_title = st.text_input("Task title", key="task_title")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20, key="duration",
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority")
        scheduled_time = st.time_input("Scheduled time", value=time(9), key="scheduled_time")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], key="frequency")
        st.caption("Frequency is recorded as a label; automatic recurrence is not implemented.")
        if st.form_submit_button("Add task"):
            try:
                task = Task(
                    title=task_title.strip(), duration_minutes=int(duration),
                    priority=priority, scheduled_time=scheduled_time, frequency=frequency,
                )
                pets[pet_index].add_task(task)
                st.success(f"Added {task.title} for {pets[pet_index].name}.")
            except ValueError as error:
                st.error(str(error))

    task_rows = [
        {"Pet": pet.name, "Task": task.title, "Time": task.scheduled_time.strftime("%H:%M"),
         "Minutes": task.duration_minutes, "Priority": task.priority,
         "Frequency": task.frequency, "Completed": task.completed}
        for pet in pets for task in pet.get_tasks()
    ]
    if task_rows:
        st.table(task_rows)
    else:
        st.info("No tasks yet. Add one above.")

st.subheader("Today's Schedule")
if st.button("Generate schedule", disabled=not owner.get_all_tasks()):
    st.session_state.show_schedule = True

# Rebuild from the current owner to keep a displayed plan in sync with edits.
if st.session_state.show_schedule:
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()
    if plan:
        st.table([
            {"Time": task.scheduled_time.strftime("%H:%M"),
             "Pet": scheduler.get_pet_for_task(task).name,
             "Task": task.title, "Minutes": task.duration_minutes,
             "Priority": task.priority}
            for task in plan
        ])
    else:
        st.info("No pending tasks fit today's time budget.")
    st.write(scheduler.explain_plan())
