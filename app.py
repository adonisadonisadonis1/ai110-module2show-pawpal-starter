"""Streamlit interface backed by the session's PawPal owner and pets."""

from datetime import date, time

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
plan_date = st.date_input("Plan date", value=date.today(), key="plan_date")
scheduler = Scheduler(owner)
if "completion_notice" in st.session_state:
    st.success(st.session_state.pop("completion_notice"))
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
        due_date = st.date_input("Due date", value=date.today(), key="due_date")
        st.caption("Completing daily or weekly care creates its next occurrence.")
        if st.form_submit_button("Add task"):
            try:
                task = Task(
                    title=task_title.strip(), duration_minutes=int(duration),
                    priority=priority, scheduled_time=scheduled_time, frequency=frequency,
                    due_date=due_date,
                )
                pets[pet_index].add_task(task)
                st.success(f"Added {task.title} for {pets[pet_index].name}.")
            except ValueError as error:
                st.error(str(error))

    pet_filter = st.selectbox(
        "Filter by pet", options=[None] + list(dict.fromkeys(pet.name for pet in pets)),
        format_func=lambda name: "All pets" if name is None else name, key="pet_filter",
    )
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"], key="status_filter")
    all_dates = st.checkbox("Show all dates", key="all_dates")
    completed_filter = {"All": None, "Pending": False, "Completed": True}[status_filter]
    selected_date = None if all_dates else plan_date
    visible_tasks = scheduler.sort_by_time(scheduler.filter_tasks(
        pet_name=pet_filter, completed=completed_filter, on_date=selected_date,
    ))
    pending_tasks = [task for task in visible_tasks if not task.completed]
    if pending_tasks:
        with st.form("completion_form"):
            completion_index = st.selectbox(
                "Task to complete", options=range(len(pending_tasks)), key="completion_task",
                format_func=lambda index: (
                    f"{index + 1}. {scheduler.get_pet_for_task(pending_tasks[index]).name}: "
                    f"{pending_tasks[index].title} "
                    f"({pending_tasks[index].due_date} {pending_tasks[index].scheduled_time:%H:%M})"
                ),
            )
            if st.form_submit_button("Mark complete"):
                next_task = scheduler.mark_task_complete(pending_tasks[completion_index])
                if next_task is None:
                    st.session_state.completion_notice = "Task completed."
                else:
                    st.session_state.completion_notice = (
                        f"Task completed. Next occurrence: {next_task.due_date} "
                        f"at {next_task.scheduled_time:%H:%M}."
                    )
                # Rebuild choices immediately so completed tasks cannot remain selected.
                st.rerun()

    task_rows = [
        {"Pet": scheduler.get_pet_for_task(task).name, "Task": task.title,
         "Date": str(task.due_date), "Time": task.scheduled_time.strftime("%H:%M"),
         "Minutes": task.duration_minutes, "Priority": task.priority,
         "Frequency": task.frequency, "Completed": task.completed}
        for task in visible_tasks
    ]
    if task_rows:
        st.table(task_rows)
    else:
        st.info("No tasks match these filters.")

st.subheader("Daily Schedule")
st.caption("The daily plan includes all pets; task-list filters above only change the task view.")
for warning in scheduler.detect_conflicts(plan_date):
    st.warning(warning)
st.caption("Warnings flag identical start times, including across pets. Review the listed activities before carrying out care; duration overlaps are not checked.")
if st.button("Generate schedule", disabled=not owner.get_all_tasks()):
    st.session_state.show_schedule = True

# Rebuild from the current owner to keep a displayed plan in sync with edits.
if st.session_state.show_schedule:
    plan = scheduler.generate_daily_plan(plan_date)
    if plan:
        st.table([
            {"Date": str(task.due_date), "Time": task.scheduled_time.strftime("%H:%M"),
             "Pet": scheduler.get_pet_for_task(task).name,
             "Task": task.title, "Minutes": task.duration_minutes,
             "Priority": task.priority}
            for task in plan
        ])
    else:
        st.info("No pending tasks fit the time budget for this date.")
    st.write(scheduler.explain_plan())
