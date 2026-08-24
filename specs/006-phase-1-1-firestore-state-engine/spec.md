# Feature Specification: Phase 1.1 GCP Cloud Firestore Student State Persistence Engine

**Feature Branch**: `006-phase-1-1-firestore-state-engine`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Phase 1.1 Firestore state persistence schema and client wrapper for student academic data

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student State Document Store (Priority: P1)

As the Bellmon batch execution runtime, I want to load and store student academic state documents in GCP Cloud Firestore at `students/{student_id}` so that system state, assignment tracking ledgers, grade history, and attendance records persist across sub-daily job executions.

**Why this priority**: Firestore state storage is the foundational prerequisite for all Phase 1 alert engines (grace period calculation, grade trajectory tracking, attendance deduplication).

**Independent Test**: Executing state storage unit tests reads, updates, and verifies full student document models against a Firestore emulator/mock client.

**Acceptance Scenarios**:

1. **Given** a student ID, **When** `get_student_state(student_id)` is invoked, **Then** it retrieves the parsed `StudentState` object from Firestore or returns a clean default state if not found.
2. **Given** updated student data, **When** `update_student_state(student_id, state)` is invoked, **Then** it atomically updates the document fields in Firestore at `students/{student_id}`.

---

### User Story 2 - Grade History Snapshot Ledger (Priority: P1)

As a grade trajectory monitor, I want to append dated grade snapshot records to `courses.{course_id}.history` in Firestore so that historical percentage snapshots are available for $[t-10, t-7]$ day velocity drop comparisons.

**Why this priority**: Required to calculate grade velocity drops over time without relying on ephemeral in-memory state.

**Independent Test**: Invoking the grade history update method appends a new snapshot entry `{"date": "YYYY-MM-DD", "percentage": Float, "letter_grade": String}` without overwriting existing history entries.

**Acceptance Scenarios**:

1. **Given** daily course percentage updates, **When** persisting course state, **Then** the current grade snapshot is appended to the course history array with the current date timestamp.
2. **Given** a historical window query request for date range $[t-10, t-7]$, **When** historical snapshots are queried, **Then** the nearest grade percentage within the window is returned.

---

### User Story 3 - Session Cookie Storage & Retrieval (Priority: P2)

As a PowerSchool browser scraper, I want to store and retrieve encrypted SAML session cookies (`psaid`) in Firestore under `students/{student_id}.session_cookies` so that Playwright can reuse existing sessions and avoid unnecessary login overhead.

**Why this priority**: Reduces SAML SSO login frequency and improves execution speed and reliability.

**Independent Test**: Storing session cookies updates `session_cookies.psaid` and `session_cookies.updated_at`; retrieving reads the stored cookies successfully.

**Acceptance Scenarios**:

1. **Given** valid session cookies after PowerSchool scraping, **When** session cookies are saved, **Then** Firestore updates `session_cookies` with the cookie payload and ISO timestamp.
2. **Given** stored session cookies, **When** PowerSchool scraper initializes, **Then** it reads stored cookies from Firestore to attempt session reuse.

---

### Edge Cases

- How does the system handle missing or uninitialized student Firestore documents?
  - Automatically initializes a default `StudentState` structure with empty courses, tracked assignments, and attendance events.
- What happens if concurrent batch executions attempt to write to Firestore?
  - Uses Firestore atomic field transformations and merge updates (`merge=True`) to prevent overwriting parallel field updates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a Firestore client wrapper in `src/storage/firestore.py` managing GCP Firestore connections.
- **FR-002**: System MUST define schema data models (`StudentState`, `CourseState`, `TrackedAssignment`, `AttendanceEvent`, `SessionCookies`) in `src/storage/models.py`.
- **FR-003**: System MUST store student documents at path `students/{student_id}` in Google Cloud Firestore.
- **FR-004**: System MUST provide methods for reading (`get_student_state`) and updating (`update_student_state`) student records.
- **FR-005**: System MUST maintain grade history snapshots per course in `courses.{course_id}.history` array.
- **FR-006**: System MUST store and retrieve encrypted PowerSchool SAML session cookies.
- **FR-007**: System MUST provide a mock/emulator client mode for local development and unit testing without requiring GCP credentials.

### Key Entities

- **StudentState**: Master document structure containing `student_id`, `last_synced_at`, `session_cookies`, `courses`, `tracked_assignments`, and `attendance_events`.
- **CourseState**: Structure containing `name`, `current_percentage`, `letter_grade`, and `history` list of `{"date", "percentage", "letter_grade"}` objects.
- **TrackedAssignment**: Structure containing `title`, `course_id`, `due_at`, `submission_type`, `status`, `first_detected_missing`, and `alert_dispatched`.
- **AttendanceEvent**: Structure containing `date`, `period`, `course`, `code`, and `notified` status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Firestore read and write operations complete within 200ms per student record.
- **SC-002**: Document schema validation catches malformed state objects before writing to Firestore.
- **SC-003**: Unit test suite for Firestore storage layer achieves 100% pass rate using local mock/emulator mode.
