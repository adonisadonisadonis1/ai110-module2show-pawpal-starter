# PawPal+

PawPal+ helps a busy pet owner organize care across multiple pets. A Streamlit
interface and a standalone CLI share the same Python backend, so task management,
daily planning, recurrence, and conflict warnings use one set of rules.

## Features

- Manage multiple pets and add care tasks with a description, date, time,
  duration, priority, and daily/weekly/once frequency.
- View tasks in chronological order and filter by pet, completion status, or date.
- Generate a daily plan across all pets within an available-minute budget.
- See advisory warnings when pending tasks share an exact date and start time.
- Mark tasks complete; daily and weekly tasks automatically create one new pending
  occurrence for the same pet, keeping the completed original as history.
- Retain pets and tasks through Streamlit reruns in the current session.
- Run the CLI demo and automated backend/UI tests without opening a browser.

## Getting Started

Use Python 3.9 or newer. The project was verified with Python 3.9.6.

```bash
git clone https://github.com/adonisadonisadonis1/ai110-module2show-pawpal-starter.git
cd ai110-module2show-pawpal-starter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`.
Open the local URL printed by Streamlit (normally `http://localhost:8501`).
For a terminal-only demonstration, run `python main.py` from the repository folder.

## Demo Walkthrough

1. Enter an owner name and daily time budget, then select **Save owner**.
2. Add Mochi as a dog and Luna as a cat using **Add pet**. Both appear in the pet
   table and remain available after other actions.
3. In the task form, choose Mochi and add a daily Morning walk for today at 08:00,
   lasting 20 minutes. Add Luna's daily Breakfast at the same date/time for
   10 minutes. Add a weekly Evening grooming for Mochi at 18:00 for 15 minutes.
   Tasks can be entered out of order; the task table sorts by date and time.
4. Choose **Plan date**. Use **Filter by pet**, **Filter by status**, and
   **Show all dates** to inspect care tasks. Pet-name filtering includes all pets
   with that name if names are repeated. Filters affect the task table and
   completion choices; the daily plan still covers every pet.
5. Review the warning identifying the 08:00 clash, with both pet names and task
   descriptions. It is advisory and remains visible even if a conflicting task
   would be excluded by the daily budget or hidden by a task-table filter.
6. Select **Generate schedule** to see pending tasks for the selected date in
   time order. Tasks exceeding the remaining budget are skipped; the explanation
   shows selected task count and total minutes. Conflicts are not automatically
   resolved or removed.
7. Choose Morning walk under **Task to complete**, then select **Mark complete**.
   A success message gives its next date/time. The original becomes completed and
   tomorrow's pending occurrence is attached to Mochi. Use the Completed filter
   to see history, or select tomorrow's Plan date to see the new occurrence.
   Completing weekly care similarly creates its next occurrence seven days later.

The CLI independently demonstrates unordered input, sorting, filtering,
conflict warnings, daily/weekly completion, and the remaining plan. Captured
output from `python main.py` (dates change with the demo run):

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

## Smarter Scheduling

| Feature | Backend method | Rule |
| --- | --- | --- |
| Sorting | `Scheduler.sort_by_time(tasks=None)` | New list ordered by due date and time; equal slots preserve insertion order. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None, on_date=None)` | Combine optional case-insensitive pet name, completion status, and due date. `None` leaves a filter unrestricted. |
| Daily planning | `Scheduler.generate_daily_plan(on_date=None)` | Collect all pets' tasks through `Owner.get_all_tasks()`, select pending tasks due on the day, sort, then admit those fitting the remaining budget. Defaults to today. |
| Conflict warnings | `Scheduler.detect_conflicts(on_date=None)` | One warning for each exact date/time group containing multiple pending tasks, within one pet or across pets. Defaults to checking all dates. |
| Completion and recurrence | `Scheduler.mark_task_complete(task, completed_on=None)` | Complete once, retain history, and attach the next daily/weekly occurrence to its owning pet; once-only tasks have no successor. |

Tasks use `datetime.date` and `datetime.time`, avoiding ambiguous time strings.
Sorting costs O(n log n). Filtering and conflict grouping take expected O(n) time
and O(n) temporary storage. An explicit grouping loop is easier to follow than
nested pairwise comparisons and avoids O(n²) conflict checking.

Recurrence uses `timedelta(days=1)` or `timedelta(days=7)` from the later of the
due date and completion date. Completing today's daily task creates tomorrow's
task; late completion moves the next occurrence forward without producing a
backlog, and early completion advances from the original due date. Late weekly
completion can shift the weekday. `completed_on` defaults to today; changing the
UI's Plan date does not change the actual completion date. Repeating completion
creates no duplicate successors.

Application code should call `Scheduler.mark_task_complete()`. The lower-level
`Task.mark_complete()` returns a successor but cannot attach it to a pet itself.
Completion rejects unknown tasks and task instances shared across pets; create a
separate Task instance for each pet. `Task.update()` supports validated description,
duration, and priority edits through the Python API; the UI currently adds and
completes tasks rather than editing them.

## Architecture

| File | Purpose |
| --- | --- |
| `pawpal_system.py` | Four dataclasses: Owner, Pet, Task, and Scheduler. |
| `app.py` | Streamlit forms, session state, sorted/filtered views, warnings, and completion. |
| `main.py` | Reproducible CLI workflow using the same backend methods. |
| `tests/` | Backend, algorithm, and Streamlit AppTest verification. |
| `diagrams/uml_final.mmd` | Final Mermaid architecture with attributes, methods, and relationships. |
| `diagrams/uml_draft.mmd` | Original Phase 1 blueprint retained for comparison. |
| `reflection.md` | Design decisions, tradeoffs, AI strategy, and verification. |

Owner holds pets; each Pet holds task occurrences. Scheduler references an Owner,
retrieves all tasks from it, and keeps a daily plan containing the original Task
objects. Task creates a successor; Scheduler attaches that successor to the correct
pet. `st.session_state.owner` keeps this object graph during session reruns.
The final UML includes new date/time/frequency attributes, aggregation and algorithm
methods, optional parameters/return types, and the recurrence dependency.
`diagrams/uml.mmd` mirrors the final source for the starter's expected path.

Open [the final UML](diagrams/uml_final.mmd) in a Mermaid-capable editor to render
it. Its `sort_by_time` parameter is shown as a nullable list of Task objects.

## Testing PawPal+

Activate the environment and run:

```bash
python -m pytest
```

The suite covers task addition/completion and validation, multi-pet aggregation,
chronology and stable ties, combined filters, zero/exact budgets, empty inputs,
recurrence across leap days and year boundaries, duplicate completion, ownership,
exact-time conflicts, rejected-operation atomicity, and collection isolation.
Streamlit AppTest checks form submissions, session reruns, date entry, sorted and
filtered tables, cross-pet warnings, and recurring completion in the final UI.

Captured output from `python -m pytest`:

```text
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/adonis/Documents/ChatGPT/project 2/pawpal-starter
collected 36 items

tests/test_algorithms.py ............                                    [ 33%]
tests/test_app.py ....                                                   [ 44%]
tests/test_pawpal.py ....................                                [100%]

============================== 36 passed in 1.79s ==============================
```

**Confidence Level: ★★★★☆ (4/5).** All 36 tests pass for the current supported
rules. AppTest exercises Streamlit interactions; it does not replace a real-browser
end-to-end test or large-data performance testing.

## Current Limits

- Data is in memory for one session; a browser reload, new session, or server
  restart can reset it. There is no database, account system, or notification service.
- Conflict checks compare identical start times, not overlapping durations, and
  warnings do not reschedule tasks automatically.
- Tasks are selected chronologically, not by priority or owner preferences.
  Those attributes are stored; preference controls are not exposed in the UI.
- Dates and times are local values without timezone/DST conversion. The daily
  plan includes exactly the selected due date; overdue care is visible through
  **Show all dates** but is not automatically carried forward into today's plan.
