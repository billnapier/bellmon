# Feature Specification: Academic & Workload Sentinel (Bellmon)

**Feature Branch**: `002-academic-sentinel`  
**Created**: 2026-08-20  
**Status**: Draft  
**Input**: User description: "Ingest requirements from docs/prd.md, user flows from docs/cujs.md, and phases from docs/roadmap.md."

## Clarifications

### Session 2026-08-20
- Q: Are there any critical functional ambiguities in the ingested PRD, CUJ, and Roadmap specifications? → A: No critical ambiguities detected; all threshold metrics (36h grace period, 4.0% velocity drop, Sun 6pm digest) are fully ratified.


## User Scenarios & Testing *(mandatory)*

### User Story 1 - Digital Missing Assignment Grace Period (Priority: P1)

As a student and parent, I want a 36-hour grace period for overdue digital assignments before parents are notified, so that students have time to self-advocate and submit work without immediate parental alerts.

**Why this priority**: Core to preserving student autonomy and avoiding unnecessary friction at home over freshly overdue digital tasks.

**Independent Test**: Can be tested by creating an overdue digital assignment state; verify state enters a 36-hour grace period without firing an alert, resolves silently if submitted within 36 hours, and fires an alert only after 36 hours.

**Acceptance Scenarios**:

1. **Given** Canvas reports `missing: true` for a digital submission (`submission_types` = `online_upload`) and PowerSchool has no grade entered (`-`), **When** scheduled sync runs, **Then** state is set to `GRACE_PERIOD` with `first_detected_missing` timestamp and no parent notification is sent.
2. **Given** an assignment is in `GRACE_PERIOD`, **When** student submits the assignment within 36 hours, **Then** state updates to `RESOLVED` with zero notifications.
3. **Given** an assignment is in `GRACE_PERIOD`, **When** 36 hours elapse without submission or score entry, **Then** system elevates state to `ALERT_DISPATCHED` and fires a P0 push alert.

---

### User Story 2 - Confirmed Missing Work Direct Alerting (Priority: P1)

As a parent, I want immediate alerts when an assignment is explicitly confirmed missing by a teacher in the gradebook, so that I can intervene promptly on verified missing work.

**Why this priority**: High urgency; bypasses grace period when missing status is already explicitly recorded by the teacher in PowerSchool.

**Independent Test**: Can be tested by setting PowerSchool status to `isMissing: true` or `score: 0`; verify an immediate P0 push notification is dispatched during the next sync run.

**Acceptance Scenarios**:

1. **Given** PowerSchool flags an assignment as `isMissing: true` or `score: 0`, **When** daily ingestion runs, **Then** system bypasses the 36-hour grace period and dispatches an immediate P0 push notification with course name, assignment title, due date, and point loss.
2. **Given** Canvas reports `missing: false` but PowerSchool reports `isMissing: true`, **When** sync runs, **Then** system fires a P0 push alert for confirmed missing work.

---

### User Story 3 - Paper & In-Class Work False-Positive Suppression (Priority: P1)

As a student, I want Canvas missing flags on physical paper or in-class work to be suppressed when recorded in PowerSchool, so that false alarms do not bother my parents.

**Why this priority**: Critical noise-reduction feature ensuring system credibility and student trust.

**Independent Test**: Can be tested by marking Canvas `missing: true` while PowerSchool has `score > 0` or `isCollected: true`; verify alert is suppressed and logged.

**Acceptance Scenarios**:

1. **Given** Canvas reports `missing: true` for an assignment, **When** PowerSchool reports `score > 0` or `isCollected: true`, **Then** system suppresses the notification and logs `SUPPRESSED_PAPER_OR_GRADED`.

---

### User Story 4 - Significant Grade Trajectory Drop Warning (Priority: P1)

As a parent, I want alerts when a student's grade in any course drops by 4.0% or more over a rolling 7-day period, along with the specific assignment causing the drop, so that early support can be offered.

**Why this priority**: Essential proactive risk detection before end-of-term deficits develop.

**Independent Test**: Can be tested by simulating a grade drop $\ge 4.0\%$ across a 7-day window; verify system identifies the drop and isolates the impacting assignment in the P0 alert.

**Acceptance Scenarios**:

1. **Given** course grade snapshot history over 7 days, **When** current grade percentage drops by $\ge 4.0\%$ compared to 7 days prior, **Then** system calculates drop delta, isolates the assignment with the largest point deduction, and dispatches a P0 push alert.

---

### User Story 5 - Sunday Night Workload & Planning Digest (Priority: P2)

As a student and parent, I want a weekly email digest every Sunday at 6:00 PM summarizing course standings, upcoming 7-day deadlines, and warnings for heavy workload clusters ($\ge 2$ major assessments within 48 hours), so that we can plan the week effectively.

**Why this priority**: Medium priority (Phase 2 feature) focused on weekly organization and backwards planning.

**Independent Test**: Can be tested by triggering the digest pipeline with upcoming major exams within a 48-hour window; verify HTML email generation with workload clumping banner.

**Acceptance Scenarios**:

1. **Given** scheduled Sunday 6:00 PM trigger, **When** digest generator runs, **Then** system gathers course grades, upcoming 7-day deadlines, scans for $\ge 2$ major assessments (Exams, Projects, Midterms, or $\ge 50$ pts) due within 48 hours, and dispatches an HTML email digest.

---

### User Story 6 - Attendance Anomaly Detection (Priority: P3)

As a parent, I want alerts when an unexcused absence, tardy, unverified absence, or cut occurs, so that attendance issues are recognized on the day they happen.

**Why this priority**: Phase 3 feature expanding sentinel coverage into daily attendance oversight.

**Independent Test**: Can be tested by supplying period attendance codes $\in \{\text{'A'}, \text{'T'}, \text{'U'}, \text{'CUT'}\}$; verify P0 alert dispatch for unexcused events.

**Acceptance Scenarios**:

1. **Given** daily attendance records from PowerSchool, **When** period attendance contains an unexcused code ($\text{'A'}, \text{'T'}, \text{'U'}, \text{'CUT'}$), **Then** system dispatches a P0 alert detailing course, period, and code, while ignoring excused/present codes ($\text{'P'}, \text{'E'}, \text{'EX'}, \text{'ACT'}$).

---

### User Story 7 - Automated Ingestion & State Diff Sync (Priority: P1)

As a system operator, I want automated, idempotent daily ingestion and state diffing from Canvas and PowerSchool, so that student status is tracked reliably without manual app interaction.

**Why this priority**: Foundational background operational model powering all rule evaluators.

**Independent Test**: Can be tested by executing scheduled sync runs; verify idempotent state updates and alert ledger deduplication.

**Acceptance Scenarios**:

1. **Given** scheduled sync run execution, **When** harvester ingests Canvas and PowerSchool data, **Then** state store updates snapshots, executes rule evaluators, and records dispatched alerts in the ledger to prevent duplicate notifications.

---

### Edge Cases

- What happens when Canvas and PowerSchool course names or assignment titles do not match exactly? The engine normalizes titles and correlates via due dates and assignment metadata.
- What happens when a teacher updates a grade from 0 back to missing or changes a score after an alert was dispatched? The alert ledger prevents duplicate alerts while state store reflects latest values.
- What happens when API endpoints for Canvas or PowerSchool experience temporary downtime or network timeouts? System retries with exponential backoff and defers evaluation to the next scheduled run without corrupting state.
- What happens when multiple missing assignments occur simultaneously? System batches notifications or sends concise structured payloads per assignment without flooding push channels.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST ingest missing submissions, assignment details, due dates, and submission types from Canvas REST API.
- **FR-002**: System MUST ingest overall course grades, letter grades, assignment scores, and period attendance records from PowerSchool Mobile REST API.
- **FR-003**: System MUST enforce a 36-hour grace period delay before alerting on overdue digital upload assignments that lack PowerSchool scores.
- **FR-004**: System MUST suppress alerts for Canvas missing items if PowerSchool indicates score $>0$ or `isCollected: true`.
- **FR-005**: System MUST bypass grace periods and fire immediate P0 push alerts for assignments explicitly marked as missing (`isMissing: true` or `score: 0`) in PowerSchool.
- **FR-006**: System MUST track rolling 7-day course grade velocity and fire P0 push alerts when a grade drops by $\ge 4.0\%$, identifying the specific assignment responsible.
- **FR-007**: System MUST generate and send a weekly HTML email digest every Sunday at 6:00 PM with course standings, upcoming deadlines, and workload clumping warnings ($\ge 2$ major assessments within 48 hours).
- **FR-008**: System MUST monitor period attendance records and alert on unexcused codes ($\text{'A'}, \text{'T'}, \text{'U'}, \text{'CUT'}$).
- **FR-009**: System MUST record all state snapshots and dispatched alerts in an idempotent state store/ledger to prevent duplicate notifications.
- **FR-010**: All cloud infrastructure (Cloud Run services, Cloud Scheduler jobs, Firestore database, IAM bindings) MUST be declared as code using Terraform.
- **FR-011**: CI/CD deployment automation MUST be executed via GitHub Actions using Guardian (`https://github.com/abcxyz/guardian`) for policy-enforced Terraform plan and apply execution.


### Key Entities

- **Student State Snapshot**: Represents student course standings, historical grade snapshots (rolling 14 days), and sync timestamps.
- **Tracked Assignment**: Represents an assignment ingested from Canvas/PowerSchool, storing due date, submission type, missing flags, grace period timestamps, and alert dispatch state.
- **Attendance Event**: Represents a period attendance record, storing date, period number, course name, attendance code, and notification status.
- **Alert Ledger Entry**: Records dispatched notifications with unique event keys to enforce idempotency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of paper turned-in work or teacher-graded items generate zero false missing notifications.
- **SC-002**: 100% of digital missing assignments observe a minimum 36-hour buffer before parental alert dispatch.
- **SC-003**: 100% of course grade drops $\ge 4.0\%$ trigger a P0 alert specifying the impacting assignment title within 24 hours of grade recording.
- **SC-004**: 0 duplicate notifications are dispatched across sync runs for the same underlying event.
- **SC-005**: 100% of scheduled Sunday digests deliver workload clumping warnings whenever $\ge 2$ major assessments fall within a 48-hour window.
