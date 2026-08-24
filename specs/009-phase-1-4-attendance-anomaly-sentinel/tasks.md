# Tasks: Phase 1.4 Period Attendance Anomaly Sentinel

## Execution Phases

### Phase 1: Setup & Data Models

- [x] T001 Add `AttendanceCodeSeverity`, `AttendanceRecordInput`, `AttendanceEvent`, and `PendingAttendanceAlert` Pydantic models to `src/engine/models.py`.

### Phase 2: User Story 1 - Period Unexcused Absence & Class Cut P0 Detection (Priority P1)

Goal: Detect P0 urgent attendance codes (`A`, `CUT`) and generate `PendingAttendanceAlert` payloads immediately.
Test Criteria: Feeding code `A` or `CUT` produces `PendingAttendanceAlert`. Present (`P`), Excused (`E`, `EX`), and Activity (`ACT`) produce zero alerts.

- [x] T002 [P] [US1] Implement `AttendanceCodeSeverity` classification logic (`classify_code`) in `src/engine/attendance.py`.
- [x] T003 [US1] Implement core `AttendanceSentinel.evaluate_student_attendance` method in `src/engine/attendance.py`.
- [x] T004 [US1] Implement unit tests for P0 urgent detection and ignored code suppression in `tests/test_attendance.py`.

### Phase 3: User Story 2 - Attendance Alert Deduplication (Priority P1)

Goal: Suppress duplicate P0 alerts for attendance events `(date, period, course)` already recorded with `notified: true`.
Test Criteria: Evaluating an event already present with `notified: true` emits no duplicate alert.

- [x] T005 [US2] Implement deduplication ledger lookup matching `(date, period, course_name)` in `src/engine/attendance.py`.
- [x] T006 [US2] Implement unit tests for alert deduplication across sub-daily sync runs in `tests/test_attendance.py`.

### Phase 4: User Story 3 - Minor Attendance Code Queuing for Sunday Digest (Priority P2)

Goal: Log minor codes like tardies (`T`) or unverified entries (`U`) to `attendance_events` with `notified: false` without triggering immediate P0 alerts.
Test Criteria: Code `T` or `U` creates an `AttendanceEvent` with `notified: false` and zero immediate `PendingAttendanceAlert` payloads.

- [x] T007 [US3] Implement minor attendance code handling for `P1_DIGEST` severity in `src/engine/attendance.py`.
- [x] T008 [US3] Implement unit tests for minor attendance code queuing in `tests/test_attendance.py`.

### Phase 5: Polish & Integration

- [x] T009 Implement edge case handling (retrospective update of code from `A` to `E`) in `src/engine/attendance.py`.
- [x] T010 Run full test suite and verify 100% pass rate in `tests/test_attendance.py`.
