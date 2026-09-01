# Tasks: Phase 1.9 Daily Evening Homework & Deadline Snapshot

**Feature Branch**: `017-phase-1-9-daily-homework-snapshot`  
**Status**: Ready for Implementation  

## Tasks

### Phase 1: Foundational & Data Models
- [x] T001 Define data models (`HomeworkSnapshotPayload`, `UpcomingDeadlineItem`, `GracePeriodSnapshotItem`, `RecentlyCompletedItem`) in `src/notifications/models.py`

### Phase 2: Snapshot Generator Engine
- [x] T002 Implement `HomeworkSnapshotGenerator` telemetry collection, 24-48h window deadline filter, grace period item collector, and dispatch ledger idempotency in `src/notifications/homework_snapshot.py`

### Phase 3: HTML Email Renderer
- [x] T003 Implement `compile_homework_snapshot_email` in `src/notifications/renderer.py` featuring red grace period alert banner, upcoming deadline cards, and recently completed work section

### Phase 4: Unit Testing & Verification
- [x] T004 Implement unit tests in `tests/test_homework_snapshot.py` covering window bounds `[now, now+48h]`, grace period item alerts, Canvas authority submission overrides, HTML rendering, and idempotency

### Phase 5: Status & Documentation
- [x] T005 Export generator and renderer methods in `src/notifications/__init__.py` and update `specs/STATUS.md`

