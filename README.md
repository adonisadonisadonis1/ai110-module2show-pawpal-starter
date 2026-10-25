# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Streamlit Integration

Run the connected UI from the repository directory:

```bash
source .venv/bin/activate
streamlit run app.py
```

The app creates `st.session_state.owner` only when the key is absent, so the same
Owner, its Pets, and their Tasks survive widget-triggered reruns. Save owner details,
submit **Add pet**, then select that pet in the task form and submit **Add task**.
The forms call `Owner.add_pet()` and `Pet.add_task()` with real backend objects.
Pet and task tables render after submission so changes appear immediately.
**Generate schedule** calls the existing Scheduler for all of the owner's pets.
A displayed schedule refreshes from the current model after subsequent edits.

Session state is temporary: a new session or browser reload can reset it. This
phase adds no database or new scheduling rules. The integration tests exercise
pet/task creation, selected-pet assignment, schedule display, state across reruns,
and blank-input handling with Streamlit's AppTest. All seven backend/UI tests pass
with `python -m pytest`.

## Phase 2 Implementation Summary

`pawpal_system.py` implements four in-memory dataclasses. `Task` stores a description
(`title`), duration in minutes, scheduled time, frequency, priority, and completion
status. It supports validated edits and completion. `Pet` manages its tasks;
`Owner` manages multiple pets and combines their tasks through `get_all_tasks()`.
`Scheduler` calls that Owner method, orders pending tasks by scheduled time, and
includes tasks that fit the remaining daily time budget. The plan retains the
original task objects, and `get_pet_for_task()` identifies the pet for each entry.
Methods have one-line docstrings.

This is a basic CLI-first implementation. Frequency is descriptive metadata;
there is no date-based recurrence engine. Priority and owner preferences are stored
for later scheduling refinements but do not affect selection yet. Scheduled times
are ordering labels; overlap resolution is not implemented. State lasts only for
the current process. The Streamlit starter was unchanged during Phase 2; the integration above connects it in the next phase.

Run the demo from the repository directory:

```bash
source .venv/bin/activate
python main.py
```

## 🖥️ Sample Output

Captured from running `python main.py`:

```text
Today's Schedule
Owner: Jordan | Pets: Mochi, Luna
08:00 | Mochi | Morning walk | 20 min | high priority | daily
08:30 | Luna | Breakfast | 10 min | high priority | daily
18:00 | Mochi | Evening grooming | 15 min | low priority | daily
Planned 3 tasks totaling 45 of 60 available minutes. Tasks are ordered by scheduled time; completed tasks and tasks that exceed the remaining budget are skipped.
```

## 🧪 Testing PawPal+

```bash
# Run the Phase 2 tests:
python -m pytest
```

Phase 2 verification: `python -m pytest -q` passed all 5 tests. These cover task
completion, task addition, multi-pet aggregation through the Owner method,
completed/over-budget task filtering, and preserving a task after an invalid edit.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
