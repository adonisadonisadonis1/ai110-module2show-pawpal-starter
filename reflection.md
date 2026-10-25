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

Pet and Task use Python dataclasses, as do Owner and Scheduler to declare their attributes without custom constructors. Each collection uses default_factory=list so instances do not share mutable lists. The Mermaid draft is saved in diagrams/uml_draft.mmd and mirrored in the starter's diagrams/uml.mmd location. All business methods are empty stubs; scheduling behavior and UI integration are outside Phase 1.

**b. Design changes**

Phase 1 AI skeleton review (before any implementation):

- The review identified a missing relationship if Scheduler only received a detached list of tasks. Scheduler now references Owner, which provides the time budget, preferences, pets, and their tasks through one consistent object graph.
- A plan containing Task objects also needs a way to identify each task's pet. Added the get_pet_for_task stub, which will traverse Owner.pets and Pet.tasks. This avoids adding a second, potentially inconsistent owner/pet reference to every task. Each Task instance should be associated with only one Pet.
- The review checked that the UML includes task editing, completion status, and an explanation method, so the design covers the README's care-tracking and explanation requirements.
- Scanning all pets and tasks is a potential bottleneck for a large collection, but it is reasonable for this small personal app. No indexing, persistence, recurring-task engine, or additional classes are needed for the initial blueprint.
- Empty methods intentionally do not validate durations, enforce ownership, rank tasks, or handle time limits yet. Those are later implementation concerns, not completed functionality.

The UML and Python signatures were checked together after these design refinements. No scheduling logic was implemented, and sections for later phases remain unanswered.

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
