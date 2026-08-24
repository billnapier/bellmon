# Feature Specification: Phase 1.2 Asymmetric System Authority & 36-Hour Grace Period Evaluation Engine

**Feature Branch**: `007-phase-1-2-asymmetric-authority-grace-period`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Phase 1.2 Asymmetric System Authority Model and 36-hour digital missing assignment grace period logic

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Canvas Digital Missing Assignment Grace Period (Priority: P1)

As a student self-advocate, I want digital missing assignments in Canvas (`submission_types: ['online_upload']`) to enter a 36-calendar-hour grace period (pausing on weekends from Friday 5 PM to Monday 8 AM) before alerting my parents so that I have time to submit the work or resolve grading glitches directly with my teacher.

**Why this priority**: Core value proposition for student autonomy, preventing immediate parental alerts for minor submission delays or teacher grading lag.

**Independent Test**: Simulating a Canvas missing assignment at timestamp $T$ verifies that status is set to `GRACE_PERIOD`, and an alert is only marked pending once 36 weekday hours have elapsed.

**Acceptance Scenarios**:

1. **Given** a new Canvas assignment flagged `missing: true` with `submission_types: ['online_upload']`, **When** evaluated, **Then** state is initialized to `status: GRACE_PERIOD` with `first_detected_missing` recorded.
2. **Given** an assignment in `GRACE_PERIOD` where 36 weekday hours have elapsed (excluding Friday 5:00 PM to Monday 8:00 AM window), **When** evaluated, **Then** assignment status transitions to `EXPIRED` and triggers a pending P0 missing alert.
3. **Given** an assignment in `GRACE_PERIOD` where student submits work before 36 hours elapse (`canvas_missing` becomes `false`), **When** evaluated, **Then** assignment transitions to `RESOLVED` with zero alert dispatched.

---

### User Story 2 - PowerSchool Confirmed Missing Direct Alert Trigger (Priority: P1)

As a parent, I want assignments explicitly marked as missing (`isMissing: true`) or assigned a score of `0` in PowerSchool SIS to trigger an immediate confirmed missing alert, bypassing the 36-hour grace period, because PowerSchool is the district official gradebook of record.

**Why this priority**: PowerSchool official gradebook entries reflect teacher-confirmed zeros or missing work that require immediate parental attention.

**Independent Test**: Passing a PowerSchool assignment with `isMissing: true` or `score: 0` immediately sets assignment status to `CONFIRMED_MISSING` and queues an alert payload without waiting 36 hours.

**Acceptance Scenarios**:

1. **Given** a PowerSchool assignment record with `isMissing: true` or `score: 0`, **When** evaluated, **Then** assignment status is set to `CONFIRMED_MISSING` and queued for P0 email alert dispatch.

---

### User Story 3 - Paper Work & Non-Digital Missing Suppression (Priority: P2)

As a student, I want Canvas missing alerts for physical assignments (`submission_types` matching `on_paper` or `none`) to be suppressed so that I am not falsely flagged for work handed in physically in class that is not submitted digitally.

**Why this priority**: Eliminates false alarms caused by Canvas marking paper assignments as missing when students hand them in physically.

**Independent Test**: Submitting a Canvas missing assignment with `submission_types: ['on_paper']` results in status `SUPPRESSED` and creates no pending alert.

**Acceptance Scenarios**:

1. **Given** a Canvas missing assignment with `submission_types` equal to `['on_paper']` or `['none']`, **When** evaluated, **Then** engine suppresses the Canvas alert and defers strictly to PowerSchool gradebook updates.

---

### Edge Cases

- What happens when an assignment is due on Friday at 11:59 PM?
  - The grace period clock starts on Saturday at 00:00, but pauses from Friday 5:00 PM until Monday 8:00 AM. Weekend hours do not consume the 36-hour budget.
- How does the engine handle title mismatches between Canvas and PowerSchool?
  - Pure Asymmetric System Authority Model: Canvas and PowerSchool entities are tracked completely independently without cross-system string matching.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `AsymmetricAuthorityEngine` in `src/engine/authority.py`.
- **FR-002**: System MUST evaluate digital Canvas missing assignments (`online_upload`) using a 36-calendar-hour timer.
- **FR-003**: System MUST pause 36-hour grace period calculations during weekends (Friday 17:00:00 to Monday 08:00:00 local time).
- **FR-004**: System MUST immediately flag PowerSchool assignments with `isMissing: true` or `score: 0` as `CONFIRMED_MISSING`.
- **FR-005**: System MUST suppress Canvas missing assignments with non-digital submission types (`on_paper`, `none`).
- **FR-006**: System MUST persist assignment status transitions (`NEW` -> `GRACE_PERIOD` -> `EXPIRED` / `CONFIRMED_MISSING` / `RESOLVED` / `SUPPRESSED`) in Firestore `tracked_assignments`.
- **FR-007**: System MUST generate structured `PendingMissingAlert` records for all `EXPIRED` and `CONFIRMED_MISSING` assignments.

### Key Entities

- **AssignmentStatus**: Enum (`NEW`, `GRACE_PERIOD`, `EXPIRED`, `CONFIRMED_MISSING`, `RESOLVED`, `SUPPRESSED`).
- **PendingMissingAlert**: Structure containing `assignment_id`, `title`, `course_id`, `due_at`, `source` (`CANVAS_GRACE_EXPIRED` vs `POWERSCHOOL_CONFIRMED`), `points_possible`, and `detected_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 36-hour grace period timer calculation accurately excludes weekend windows in 100% of test cases.
- **SC-002**: 100% of non-digital Canvas missing assignments (`on_paper`, `none`) are suppressed without emitting alerts.
- **SC-003**: PowerSchool confirmed missing items (`isMissing: true` / `score: 0`) bypass grace period and trigger alerts on the next batch run.
