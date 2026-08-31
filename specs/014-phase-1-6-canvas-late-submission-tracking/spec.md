# Feature Specification: Phase 1.6 Canvas Late Submission Tracking

**Feature Branch**: `014-phase-1-6-canvas-late-submission-tracking`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: Canvas LMS late submission ingestion (`late: true`, `submitted_at > due_at`), Firestore `late_submissions` ledger storage, and deduplication logic for CUJ-8

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Canvas Late Submission Detection & Ingestion (Priority: P1)

As a parent, I want the system to detect and record assignments submitted late on Canvas so that I have visibility into late turn-in habits even when PowerSchool does not flag the assignment as missing or late.

**Why this priority**: Canvas late submissions often precede formal grade drops or habit issues, but are invisible in PowerSchool once graded.

**Independent Test**: Ingesting a Canvas submission payload with `late: true` or `submitted_at` exceeding `due_at` logs a `LateSubmissionRecord` into Firestore.

**Acceptance Scenarios**:

1. **Given** a Canvas submission record with `late: true` OR `submitted_at > due_at`, **When** evaluated during Canvas sync, **Then** the engine creates a `LateSubmissionRecord` with course ID, assignment title, due date, submission date, and minutes late.
2. **Given** a Canvas submission record with `late: false` AND `submitted_at <= due_at`, **When** evaluated, **Then** no late submission entry is created.

---

### User Story 2 - Late Submission Ledger Deduplication & Persistence (Priority: P1)

As a system, I want late submission records to be stored idempotently in Firestore under `students/{student_id}/late_submissions` so that repeated sub-daily sync runs do not create duplicate entries or corrupt submission timestamps.

**Why this priority**: Prevents duplicate counting in frequency analytics and digest reporting.

**Independent Test**: Re-evaluating a previously logged late assignment `canvas_98765` leaves the existing record unchanged without creating duplicate Firestore documents.

**Acceptance Scenarios**:

1. **Given** a late submission for `assignment_id` already present in Firestore `late_submissions`, **When** re-processed during subsequent runs, **Then** the record is recognized as duplicate and ignored.

---

### Edge Cases

- What happens if an assignment is submitted late, but the teacher later updates the due date in Canvas to a later timestamp?
  - The record in Firestore updates `minutes_late`; if `submitted_at <= updated_due_at`, the `is_late` flag is updated to `false`.
- What happens if `submitted_at` is null or missing on a late assignment?
  - If `late: true` flag is set by Canvas, the engine uses the sync execution timestamp as `detected_late_at`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse submission metadata (`late`, `submitted_at`, `due_at`) from Canvas API responses.
- **FR-002**: System MUST identify late submissions when `late == true` OR `submitted_at > due_at`.
- **FR-003**: System MUST calculate `minutes_late` as `(submitted_at - due_at)` in minutes.
- **FR-004**: System MUST store `LateSubmissionRecord` objects in Cloud Firestore under `students/{student_id}/late_submissions/{assignment_id}`.
- **FR-005**: System MUST ensure idempotent writes so existing assignment records are not duplicated.
- **FR-006**: System MUST expose a retrieval interface to query late submissions within a specified date window `[start_date, end_date]`.

### Key Entities

- **LateSubmissionRecord**: Structure containing `assignment_id`, `course_id`, `course_name`, `title`, `due_at`, `submitted_at`, `minutes_late`, and `detected_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Canvas submissions with `late: true` or `submitted_at > due_at` are captured as `LateSubmissionRecord` entries in Firestore.
- **SC-002**: Zero duplicate records are created across repeated sub-daily sync runs for the same assignment ID.
- **SC-003**: Timely assignments (`submitted_at <= due_at` and `late == false`) produce 0 late submission records.
