# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. Enter their name, daily time available, and care preferences, then add a pet with a name and species.
2. Add or edit a pet's care tasks, such as a walk or feeding, with a title, duration in minutes, and low/medium/high priority.
3. Generate and view today's care plan across their pets, with an explanation of how time, priorities, and preferences influenced it.

The initial design uses four classes:

| Class | Attributes | Methods and responsibility |
| --- | --- | --- |
| Owner | name, available_minutes, preferences, pets | add_pet and get_pets manage the owner's pet relationships and supply planning constraints. |
| Pet | name, species, tasks | add_task and get_tasks associate care tasks with the correct pet. |
| Task | title, duration_minutes, priority, completed | update edits task details; mark_complete records completion. |
| Scheduler | owner, daily_plan | generate_daily_plan selects and orders tasks; get_daily_plan retrieves the plan; get_pet_for_task identifies the pet for a selected task; explain_plan describes planning decisions. |

One owner can have zero or more pets, and each pet can have zero or more tasks. Each pet belongs to one owner and each task belongs to one pet in this design. A scheduler references one owner and uses that owner's pets and tasks. Its plan refers to existing Task objects rather than copying them. These ownership rules are design contracts; validation is deferred.

Pet and Task use Python dataclasses, as do Owner and Scheduler to declare their attributes without custom constructors. Each collection uses default_factory=list so instances do not share mutable lists. The Mermaid draft is saved in diagrams/uml_draft.mmd and mirrored in the starter's diagrams/uml.mmd location. At that Phase 1 checkpoint, all business methods were empty stubs; later phases implemented behavior and integrated the UI.

**b. Design changes**

Phase 1 AI skeleton review (before any implementation):

- The review identified a missing relationship if Scheduler only received a detached list of tasks. Scheduler now references Owner, which provides the time budget, preferences, pets, and their tasks through one consistent object graph.
- A plan containing Task objects also needs a way to identify each task's pet. Added the get_pet_for_task stub, which will traverse Owner.pets and Pet.tasks. This avoids adding a second, potentially inconsistent owner/pet reference to every task. Each Task instance should be associated with only one Pet.
- The review checked that the UML includes task editing, completion status, and an explanation method, so the design covers the README's care-tracking and explanation requirements.
- Scanning all pets and tasks is a potential bottleneck for a large collection, but it is reasonable for this small personal app. No indexing, persistence, recurring-task engine, or additional classes are needed for the initial blueprint.
- Empty methods intentionally do not validate durations, enforce ownership, rank tasks, or handle time limits yet. Those are later implementation concerns, not completed functionality.

The draft UML and Python signatures were checked together at the Phase 1 checkpoint before scheduling logic was implemented.

The final architecture adds Task.scheduled_time, frequency, and due_date;
Owner.get_all_tasks(); and Scheduler sorting, filtering, completion, and conflict
methods. Task.mark_complete() now returns an optional successor, while
Scheduler.mark_task_complete() validates ownership and registers that successor.
The final UML is saved in diagrams/uml_final.mmd and mirrored in diagrams/uml.mmd;
diagrams/uml_draft.mmd preserves the starting design. Phase 6 connects these
existing methods to the UI without changing backend scheduling rules.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

In Phase 4 the scheduler considers the selected due date, completion status, and
the owner's available minutes. It sorts eligible tasks by date/time, then admits
each task that fits the remaining budget. Pet and status filters can narrow the
view independently. Priority and owner preferences are retained as data but do
not change ranking yet. Restricting the plan to its selected date prevents a
new recurring occurrence from appearing in today's plan.

**b. Tradeoffs**

Phase 4 checks exact date/time matches rather than overlapping durations. Grouping
pending tasks in a dictionary keyed by (due_date, scheduled_time) is easy to read
and takes expected O(n) time, compared with O(n²) pairwise comparisons. A group
with several tasks produces one readable warning listing every affected pet and
task. This detects obvious clashes without blocking the plan, but an 08:00 walk
lasting 30 minutes and an 08:15 feeding will not trigger a warning. A regression
test records that deliberate limitation.

Recurrence creates only the next occurrence when completing a task, keeping the
completed original as history. Scheduling from the later of due date and completion
date avoids an overdue backlog; the tradeoff is that completing a weekly task late
can shift its weekday. Repeated completion is a no-op to avoid duplicate future
tasks. Application code uses Scheduler.mark_task_complete() to both complete the
task and attach its returned occurrence to the same pet.

For the algorithm review, a separate planning chat compared dictionary grouping
with nested pair checks. The implementation keeps an explicit grouping loop and
warning-building loop for readability rather than compressing all work into one
expression. Sorting uses Python's stable sorted() with a lambda key and returns
a new list, so displaying a sorted view does not change the pets' task lists.
Name filtering intentionally matches all pets sharing a name; object identity is
used when completing a specific task so it attaches to the correct pet.

The follow-up review of the completed conflict method suggested iterating through
pets and their tasks directly instead of building a separate task-to-pet map and
filtered list. I accepted that change: it removes intermediate allocations while
keeping the same expected O(n) runtime. The review also reproduced incorrect
labels when one Task instance was shared by two pets. Direct iteration fixes the
labels, and completion now rejects ambiguous ownership before modifying the task.
Two additional regression tests verify this case and separate, equal-valued tasks
belonging to pets with the same name. The full suite passed 19 tests.

---

## 3. AI Collaboration

**a. How you used AI**

For Phase 2, AI helped turn the four class skeletons into working Python,
add scheduled times and frequency to Task, build a two-pet CLI demo, and draft
quick pytest checks. The most useful requirement was that Scheduler must retrieve
all tasks through Owner.get_all_tasks(). I accepted that structure because it
keeps knowledge of the pets in Owner and makes the scheduler work across pets.
I also accepted readable terminal rows with the time, pet name, description,
duration, priority, and frequency, and one-line method docstrings.

Automatic multi-file editing was effective for keeping class implementations,
CLI examples, tests, and documentation aligned. Separate planning chats for
Phase 4 algorithms and Phase 5 testing kept algorithm choices apart from test
coverage discussions. The algorithm chat compared grouping and pairwise conflict
checks; the testing chat challenged happy-path coverage with budget boundaries,
stale plans, and leap-day recurrence. Keeping those reviews focused made it easier
to evaluate suggestions against one phase's goal instead of mixing new features
into verification.

In Phase 6, AI compared the backend with the original UML and identified missing
attributes, aggregation, optional return types, and recurrence relationships.
It also helped replace starter README prompts with instructions describing
features that actually exist. Streamlit AppTest was useful for checking that UI
filters, warnings, and completion call the existing logic correctly.

**b. Judgment and verification**

The Phase 1 blueprint exposed each pet's tasks but lacked an Owner method for
aggregating them. For Phase 2, that design was revised to add get_all_tasks(),
rather than letting Scheduler plan from a single pet. The implementation also
uses object identity when finding a task's pet, so two pets can have distinct
tasks with identical values. Advanced recurrence and preference-ranking behavior
were kept out of this basic implementation; frequency and preferences are stored
without claiming that those features work.

Verification used the real output of python main.py: two pets and three tasks
appeared in chronological order. python -m pytest -q passed five tests. In
addition to the required completion and task-addition checks, a test wraps
Owner.get_all_tasks() and confirms Scheduler calls it and includes both pets'
tasks. Other checks cover completed/over-budget tasks and an invalid edit that
must leave the original task unchanged. The captured demo output is in README.md.
The Streamlit UI and Phase 1 UML draft were not changed in Phase 2.

One suggestion I modified was the recurrence policy from the algorithm planning
chat: it proposed preserving a weekly task's weekday after late completion. I kept
the simpler rule of advancing from the later of due date and completion date,
creating only one successor, and documented that late completion can shift the
weekday. This kept the initial design small and made its behavior explicit.
I accepted the later suggestion to simplify conflict detection by iterating pets
and tasks directly, removing a separate task-to-pet mapping. The shared-task edge
case from that review became an ownership guard and a regression test.

Human oversight means checking outcomes, not just accepting plausible code.
The explicit phase boundaries, expected task orders and dates, actual pytest
output, and honest README limits were the acceptance criteria. The UI originally
said recurrence was unimplemented even after the backend supported it; Phase 6
removed that stale text and added completion controls using the Scheduler API.
The final UI tests verify a successor is created for the right pet and can be
viewed on the following day.

---

## 4. Testing and Verification

**a. What you tested**

Phase 5 planned five behavior groups: task/pet management, chronological daily
planning, filtering, recurrence, and exact-time conflicts. The core suite in
tests/test_pawpal.py now includes explicit sorting, next-day daily recurrence,
and duplicate-time warning checks alongside empty-owner/empty-pet handling,
midnight and end-of-day times, zero and exact budgets, skipping an oversized task
after earlier work, independent collections, invalid durations, and rejected
completion leaving state unchanged. The recurrence check crosses leap day and
verifies the next occurrence retains its duration, priority, time, and pet.

A separate testing chat reviewed existing coverage and proposed boundary cases.
I accepted the partial-budget and stale-plan checks because they can expose bugs
that a successful three-task demo would miss. Tests assert explicit expected
results rather than reimplement sorting or date arithmetic. Parametrization runs
one behavior with several meaningful inputs, such as zero/exact budgets or bad
durations. Identity checks with `is` distinguish the original task from a newly
created occurrence and confirm the correct pet holds that exact new object.

The complete python -m pytest run passed 34 tests, including the earlier algorithm
and Streamlit integration tests. No failures occurred during the Phase 5 runs,
and no backend or UI changes were needed. The successful full terminal output is
saved in the README. Phase 6 adds two UI integration checks, bringing the final
suite to 36 passing tests. These exercise sorted/filtered task views, warnings,
recurring completion, future-date plans, and task due-date entry.

**b. Confidence**

Confidence Level: ★★★★☆ (4/5). The tests provide good confidence in the current
in-memory rules, including boundary conditions and recurrence without duplicate
successors. They do not establish production reliability for every input.
Exact-start-time conflicts are intentionally narrower than duration overlaps;
persistence across browser sessions and timezone/DST behavior are not supported.
With more time, I would verify larger task collections and real-browser workflows,
and test overlap/timezone behavior if those features are introduced. No later-phase
features or UML revisions were added during this testing phase.

---

## 5. Reflection

**a. What went well**

The strongest result is that the CLI and UI share the same backend. Owner provides
one aggregation method across pets, Scheduler owns planning decisions, and the UI
only collects input and presents results. The final interface exposes the sorting,
filtering, conflict warnings, and recurrence that were already verified in the CLI.
The history of the draft UML, final UML, tests, and reflections makes the design's
evolution understandable to another reader.

**b. What you would improve**

A future iteration could add saved data, task editing in the UI, duration-overlap
checks, and clearer treatment of overdue care. Before adding preference ranking or
timezone support, I would define concrete examples and expected behavior, then
extend tests. I would also run real-browser usability checks with a pet owner and
measure larger task collections. These are future improvements, not features
claimed by the current app.

**c. Key takeaway**

Being the lead architect means setting scope, choosing understandable rules,
and insisting that the diagram, code, UI, tests, and documentation describe the
same system. AI can quickly propose algorithms and make coordinated edits, but
speed does not settle product choices such as recurrence policy or whether a
warning should block a schedule. Those decisions need explicit tradeoffs and
observable acceptance checks. Separate phase-focused chats helped keep each
review narrow; the main implementation remained responsible for integrating and
verifying the decisions. A passing test suite supports confidence, while honest
limits prevent a polished interface from promising behavior the system lacks.
