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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
