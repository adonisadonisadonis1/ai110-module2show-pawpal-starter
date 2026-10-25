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
and blank-input handling with Streamlit's AppTest. The integration was verified with seven backend/UI tests; Phase 4 adds algorithm
checks to the same suite, runnable with `python -m pytest`.

## Phase 2 Implementation Summary

`pawpal_system.py` implements four in-memory dataclasses. `Task` stores a description
(`title`), duration in minutes, scheduled time, frequency, priority, and completion
status. It supports validated edits and completion. `Pet` manages its tasks;
`Owner` manages multiple pets and combines their tasks through `get_all_tasks()`.
`Scheduler` calls that Owner method, orders pending tasks by scheduled time, and
includes tasks that fit the remaining daily time budget. The plan retains the
original task objects, and `get_pet_for_task()` identifies the pet for each entry.
Methods have one-line docstrings.

In Phase 2, frequency was descriptive metadata. Phase 4 adds dated recurrence
and conflict warnings, documented below. Priority and owner preferences are stored
for later scheduling refinements but do not affect selection yet. Scheduled times
are ordering labels; overlap resolution is not implemented. State lasts only for
the current process. The Streamlit starter was unchanged during Phase 2; the integration above connects it in the next phase.

Run the demo from the repository directory:

```bash
source .venv/bin/activate
python main.py
```

## 🖥️ Sample Output

Captured from running `python main.py` (dates reflect the demo run):

```text
Tasks in insertion order
2026-10-25 18:00 | Mochi | Evening grooming | 15 min | weekly | pending
2026-10-25 08:00 | Mochi | Morning walk | 20 min | daily | pending
2026-10-25 12:00 | Luna | Enrichment | 5 min | once | pending
2026-10-25 08:00 | Luna | Breakfast | 10 min | daily | pending

Sorted by date and time
2026-10-25 08:00 | Mochi | Morning walk | 20 min | daily | pending
2026-10-25 08:00 | Luna | Breakfast | 10 min | daily | pending
2026-10-25 12:00 | Luna | Enrichment | 5 min | once | pending
2026-10-25 18:00 | Mochi | Evening grooming | 15 min | weekly | pending

Luna's pending tasks
2026-10-25 08:00 | Luna | Breakfast | 10 min | daily | pending
2026-10-25 12:00 | Luna | Enrichment | 5 min | once | pending

Today's Schedule
2026-10-25 08:00 | Mochi | Morning walk | 20 min | daily | pending
2026-10-25 08:00 | Luna | Breakfast | 10 min | daily | pending
2026-10-25 12:00 | Luna | Enrichment | 5 min | once | pending
2026-10-25 18:00 | Mochi | Evening grooming | 15 min | weekly | pending
Planned 4 tasks totaling 50 of 60 available minutes. Only tasks due on the selected day are considered. Tasks are ordered by scheduled time; completed tasks and tasks that exceed the remaining budget are skipped.

Conflict checks
Warning: 2026-10-25 08:00 conflict: Mochi: Morning walk; Luna: Breakfast

Complete daily walk and weekly grooming
Next daily walk: 2026-10-26 08:00
Next weekly grooming: 2026-11-01 18:00

Completed tasks
2026-10-25 18:00 | Mochi | Evening grooming | 15 min | weekly | complete
2026-10-25 08:00 | Mochi | Morning walk | 20 min | daily | complete

Today's remaining schedule
2026-10-25 08:00 | Luna | Breakfast | 10 min | daily | pending
2026-10-25 12:00 | Luna | Enrichment | 5 min | once | pending
Remaining conflicts: none
```

## Testing PawPal+

From the repository directory, activate the environment and run the full suite:

```bash
source .venv/bin/activate
python -m pytest
```

Phase 5 test plan covers five core behaviors:

| Behavior | Happy paths and edge cases |
| --- | --- |
| Task and pet management | Adding/completing tasks, independent collections, duplicate-instance prevention, safe list copies, and invalid durations/edits. |
| Chronological planning | Multiple pets, date/time order, stable ties, midnight/23:59, empty owners/pets, zero/exact budgets, skipping oversized tasks, and clearing stale plans. |
| Filtering | Pet name, pending/completed status, selected date, unmatched names, and pets sharing a name. |
| Recurrence | Daily/weekly/once, correct pet attachment, leap day and year rollover, early/late completion, duplicate completion prevention, and rejected-completion atomicity. |
| Conflict warnings | Same-pet and cross-pet duplicate times, independent conflict groups, completion clearing a clash, and exclusion of completed tasks/other dates. |

`tests/test_pawpal.py` contains the core Phase 5 checks, including explicit sorting,
daily recurrence, and duplicate-time conflict tests. `tests/test_algorithms.py`
retains the Phase 4 algorithm regressions; `tests/test_app.py` exercises Streamlit
forms and state across reruns using AppTest. Dated edge-case tests use explicit
dates, with no sleeps or dependence on the current day.

Captured output from a successful `python -m pytest` run:

```text
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/adonis/Documents/ChatGPT/project 2/pawpal-starter
collected 34 items

tests/test_algorithms.py ............                                    [ 35%]
tests/test_app.py ..                                                     [ 41%]
tests/test_pawpal.py ....................                                [100%]

============================== 34 passed in 1.36s ==============================
```

**Confidence Level: ★★★★☆ (4/5).** All 34 tests pass, covering the supported
in-memory behavior and the existing UI bridge. This is strong evidence for the
small app's current rules, not proof of every possible input. Conflict detection
intentionally checks equal start times, not duration overlaps; persistence across
browser sessions and timezone/DST scheduling are not supported or verified.
Large collections and a real-browser end-to-end workflow would need further
verification before a production reliability claim. Phase 5 changes only tests
and documentation.

## 📐 Smarter Scheduling

| Feature | Method(s) | Behavior |
| --- | --- | --- |
| Sorting | `Scheduler.sort_by_time(tasks=None)` | Returns a new list ordered by `(due_date, scheduled_time)`; equal slots preserve insertion order. An omitted list uses `Owner.get_all_tasks()`. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None, on_date=None)` | Combines optional pet-name, completion, and date filters across all pets. Names match case-insensitively; duplicate pet names match all pets with that name. `completed=None` includes both statuses. |
| Daily plan | `Scheduler.generate_daily_plan(on_date=None)` | Defaults to today, considers only pending tasks due that day, sorts them, and skips tasks exceeding the remaining time budget. |
| Conflicts | `Scheduler.detect_conflicts(on_date=None)` | Groups pending tasks by exact due date and time, returning one warning string per conflicting slot, including pet names. Covers both same-pet and cross-pet clashes; no argument checks all dates. |
| Recurrence | `Scheduler.mark_task_complete(task, completed_on=None)` and `Task.mark_complete()` | Completes the original, creates one new pending daily/weekly occurrence, and attaches it to the same pet. A once-only task creates none. Repeated completion creates no duplicates. |

Tasks now have `due_date` (default: today). Daily and weekly occurrences use
`timedelta(days=1)` and `timedelta(days=7)`, respectively. The base date is the later
of the occurrence's due date and completion date, so a task due today gets tomorrow
or next week, late completion moves the next date forward without generating a
backlog, and early completion does not move the next occurrence before its
original due date. Late weekly completion can therefore shift the weekday.
`completed_on` defaults to today and can be provided for repeatable tests.

Use `Scheduler.mark_task_complete()` for application-level completion: it finds
the owning pet and registers the new occurrence. The lower-level
`Task.mark_complete()` returns the new instance but cannot attach it to a pet by
itself. Both preserve the completed original as history. A scheduler rejects a
task it does not own or a task instance shared by multiple pets before changing it.
Use separate Task instances for each pet, even when their descriptions match.

Time values are already `datetime.time` objects, so the sort key compares them
directly. For zero-padded `HH:MM` strings, `sorted(tasks, key=lambda task:
task.time_string)` would also work; keeping typed times avoids string-format
ambiguity. Sorting costs O(n log n); filtering and exact-slot conflict grouping
cost O(n) expected time with O(n) temporary storage. Dictionary grouping avoids
comparing every pair of tasks.

Warnings are advisory: conflicting tasks remain visible and do not crash the
program. This deliberately checks equal start times, not overlapping durations,
and does not resolve conflicts automatically. Priority and owner preferences
still do not rank tasks. No UI controls or UML revisions are added in Phase 4.

Phase 4 verification: **19 tests passed**, including the existing backend/UI
checks and new tests for stable sorting, combined filters, daily/weekly/once
completion, duplicate completion, correct-pet attachment, date rollover,
early/late completion, date-aware plans, and same/cross-pet conflict warnings.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
