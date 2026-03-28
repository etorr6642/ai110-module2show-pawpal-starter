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

## 📸 Demo

![PawPal+ Demo](https://i.imgur.com/NNoskU0.gif)

## Features

- **Priority-based task sorting** — Tasks are displayed sorted by priority (1–5, highest first) so the most important care items are always visible at a glance.
- **Greedy schedule generation** — The scheduler fits as many tasks as possible into your available daily minutes using a greedy algorithm: required tasks come first, then by priority descending, then by shortest duration when priority is tied.
- **Daily recurrence tracking** — Tasks carry a `Frequency` (daily, weekly, monthly, as-needed) and a `last_completed_date`. The `is_due_today` method automatically determines whether each task should appear in today's schedule based on elapsed days.
- **Time-slot conflict detection** — The scheduler warns when two or more tasks for the same pet share the same time-of-day category (e.g., two morning tasks), reporting the combined time overlap.
- **Duplicate task detection** — A conflict warning is raised if the same task description is scheduled more than once for a pet.
- **Required-task overflow warning** — If any required task doesn't fit within available minutes, the scheduler surfaces it as an explicit warning rather than silently dropping it.
- **Remaining tasks report** — After schedule generation, tasks that didn't fit are listed separately so the owner knows what was deferred.
- **Duplicate entry prevention** — Adding a task with the same title and time-of-day slot that already exists is blocked at the UI level.
- **Deduplication across pets** — If the same `Task` object is shared across multiple pets, it is counted only once in the daily schedule to prevent double-counting time.

## Smarter Scheduling

The scheduler was updated with a few improvements to make it more useful for a pet owner.

- **Sorting by time** — Tasks are sorted by priority first, then by duration. If two tasks have the same priority, the shorter one is scheduled first. This fits more tasks into the day.
- **Recurring tasks** — Tasks now check if they are due based on their frequency. A weekly task will only show up if it has not been done in the last 7 days, and a monthly task checks for 30 days. Once a task is marked complete, it records the date so the next check is accurate.
- **Filtering** — You can filter the schedule by pet or by completion status. This makes it easier to see what still needs to be done or what one specific pet has scheduled.
- **Conflict detection** — The scheduler checks for time slot conflicts when two tasks for the same pet are scheduled in the same part of the day. It also warns if a required task did not fit in the schedule. Warnings show up at the bottom of the schedule summary.

## Testing PawPal+

To run the tests, use:

```bash
python -m pytest
```

The test suite covers the most important scheduling behaviors so that changes to the logic do not break things silently. Here is what is tested:

- **Input validation** — Tasks with an invalid priority (outside 1–5) or a negative duration raise an error immediately on creation.
- **Recurrence logic** — Daily, weekly, monthly, and as-needed tasks are checked against the correct intervals. A task that has never been completed is always due. Marking a task complete today does not skip it tomorrow.
- **Sorting correctness** — Required tasks come before optional ones. Higher priority is scheduled first. When priority is tied, the shorter task goes first so more tasks fit in the day.
- **Time budget** — Tasks that do not fit in the available time are excluded. A task that fits exactly is included.
- **Deduplication** — If the same task is assigned to two pets, it only appears once in the schedule.
- **Conflict detection** — The scheduler flags two tasks in the same category for the same pet, duplicate task descriptions, and required tasks that were dropped because time ran out.

### Confidence Level

★★★★☆

All 23 tests pass and the core scheduling behaviors work as expected. The one missing star is because the UI layer is not tested and there are real-world scenarios with multiple pets and overlapping constraints that are not covered yet. The logic holds up well for what is tested so far.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
