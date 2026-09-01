# Implementation Plan: Phase 1.9 Daily Evening Homework & Deadline Snapshot

**Feature Branch**: `017-phase-1-9-daily-homework-snapshot`  
**Status**: Approved  

## Technical Context & Architecture

The Daily Evening Homework & Deadline Snapshot operates as a scheduled weekday 7:00 PM notification. It aggregates upcoming digital deadlines within a 24 to 48 hour forward-looking window (`[now, now + 48 hours]`), active `GRACE_PERIOD` items requiring immediate evening action, and recently completed assignments (submitted in past 24 hours) into an HTML email snapshot.

### Components
1. `src/notifications/homework_snapshot.py`: Defines `HomeworkSnapshotGenerator` class and data classes (`HomeworkSnapshotPayload`, `UpcomingDeadlineItem`, `GracePeriodSnapshotItem`, `RecentlyCompletedItem`).
2. `src/notifications/renderer.py`: Extends `NotificationRenderer` with `compile_homework_snapshot_email(...)` to render responsive HTML and text fallback.
3. `src/notifications/router.py`: Dispatches email via `ResendNotificationRouter` / `NotificationRouter`.
4. `src/storage/firestore.py`: Firestore queries for upcoming deadlines, active grace period assignments, recently completed work, and dispatch ledger (`homework_snapshots`).

---

## Constitution & Architecture Checks

- **Single Source of Truth**: Uses Firestore as state store.
- **Asymmetric Grace Period & Authority**: Canvas submission status overrides PowerSchool missing flags. Active `GRACE_PERIOD` items highlight remaining window before P0 escalation.
- **Idempotency**: Daily ledger entry stored in `homework_snapshots` collection with key `student_id:YYYY-MM-DD` prevents duplicate daily dispatches.

---

## Proposed Changes

### 1. `src/notifications/homework_snapshot.py`
- Class `HomeworkSnapshotGenerator`:
  - `__init__(self, db_client=None, router=None, renderer=None)`
  - `collect_snapshot_data(student_id: str, snapshot_time: datetime) -> HomeworkSnapshotPayload`
  - `generate_and_dispatch(student_id: str, recipient_email: str, student_name: str, snapshot_time: datetime) -> DispatchResult`

### 2. `src/notifications/renderer.py`
- Add method `compile_homework_snapshot_email(payload: HomeworkSnapshotPayload) -> Tuple[str, str]`:
  - Header: "Daily Evening Homework & Deadline Snapshot"
  - Urgent Red Banner: "Pending Grace Period Action Required" (if grace items exist) listing assignment, course, original due date, hours remaining, submission link.
  - Section 1: "Due Tomorrow & Next 48 Hours" (sorted chronologically) listing course, title, portal, due date/time, submission status (`Submitted` / `Not Submitted`). Shows empty state badge if 0 items.
  - Section 2: "Recently Completed Work" (submitted in past 24 hours).

### 3. Tests
- `tests/test_homework_snapshot.py`: Unit tests for data collection, deadline filtering, grace period banners, HTML rendering, dispatch, and ledger idempotency.

---

## Verification Plan

- Run `pytest tests/test_homework_snapshot.py` to verify snapshot collection, rendering, dispatch, and idempotency.
- Run `pytest` across full suite to ensure zero regressions.
