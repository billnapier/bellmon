# Feature Specification: Phase 1.9 Daily Evening Homework & Deadline Snapshot

**Feature Branch**: `017-phase-1-9-daily-homework-snapshot`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: Weekday 7:00 PM scheduled HTML email snapshot providing a 24–48 hour forward-looking view of upcoming digital deadlines across Canvas and PowerSchool, highlighting pending grace period items needing immediate student submission (CUJ-10)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 24 to 48-Hour Digital Deadline Forward View (Priority: P1)

As a parent, I want to receive a 7:00 PM weekday snapshot listing all assignments due tonight, tomorrow, and within the next 48 hours across Canvas and PowerSchool so that my student and I can review evening homework priorities.

**Why this priority**: Helps parents and students stay organized during evening study sessions and prevents missed deadlines before school the next morning.

**Independent Test**: Triggering the snapshot generator at 7:00 PM on a Tuesday with 2 Canvas assignments due Wednesday at 11:59 PM includes both assignments in the "Due Next 48 Hours" section.

**Acceptance Scenarios**:

1. **Given** digital assignments in Canvas or PowerSchool with due dates in the window `[7:00 PM today, 7:00 PM today + 48 hours]`, **When** the snapshot generator executes at 7:00 PM, **Then** an HTML email is generated listing each assignment's course, title, portal origin, due date/time, and submission status (`Submitted` / `Not Submitted`).
2. **Given** 0 assignments due within 48 hours, **When** the snapshot generator executes, **Then** the upcoming section displays "No digital deadlines scheduled in the next 48 hours."

---

### User Story 2 - Urgent Grace Period Submission Reminders (Priority: P1)

As a parent, I want the 7:00 PM snapshot to prominently highlight any assignments currently in their 36-hour grace period so that my student is reminded to turn them in tonight before escalation to a P0 parent missing work alert.

**Why this priority**: Focuses evening effort on items closest to triggering formal missing work alerts.

**Independent Test**: Running the snapshot generator for a student with 1 assignment in `GRACE_PERIOD` state (due yesterday at 11:59 PM) displays a red alert banner "Pending Grace Period Action Required" with instructions to submit before the grace window closes.

**Acceptance Scenarios**:

1. **Given** 1 or more assignments in state `GRACE_PERIOD` in Firestore, **When** the snapshot is rendered, **Then** an urgent call-out section lists the assignment, course, original due date, and remaining grace period hours with direct Canvas/PowerSchool submission links.
2. **Given** 0 assignments in grace period, **When** rendered, **Then** the grace period call-out section is hidden or displays a clean checkmark.

---

### User Story 3 - Resend Dispatch & Alert Ledger Idempotency (Priority: P1)

As a parent, I want the 7:00 PM snapshot delivered reliably to my email with a clean, scannable layout so that I can quickly review it on mobile devices without duplicate emails.

**Why this priority**: Ensures mobile-friendly readability and avoids sending duplicate snapshot emails.

**Independent Test**: Executing the snapshot runner twice at 7:00 PM results in 1 email dispatch recorded in the Firestore `homework_snapshots` ledger collection.

**Acceptance Scenarios**:

1. **Given** a successful snapshot generation run, **When** dispatched via `ResendNotificationRouter`, **Then** an entry is logged in Firestore collection `homework_snapshots` with key `student_id:YYYY-MM-DD`.
2. **Given** an existing ledger entry for `student_id:YYYY-MM-DD`, **When** executed again on the same date, **Then** the dispatch step short-circuits to avoid duplicate emailing.

---

### Edge Cases

- What happens if an assignment was turned in at 6:30 PM (30 minutes before snapshot)?
  - Canvas/PowerSchool status synced during the 5:00 PM run will show pending unless a pre-snapshot sync occurs; the snapshot accurately reflects synced state.
- What if an assignment is marked missing in PowerSchool but submitted in Canvas?
  - Asymmetric authority rules apply: Canvas submission status takes priority and marks the item as submitted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `HomeworkSnapshotGenerator` in `src/notifications/homework_snapshot.py`.
- **FR-002**: System MUST query Firestore for assignments due within the forward window `[now, now + 48 hours]`.
- **FR-003**: System MUST query Firestore for active `GRACE_PERIOD` items for the student.
- **FR-004**: System MUST format an HTML snapshot email containing:
  - Header: "Daily Evening Homework & Deadline Snapshot"
  - Urgent Callout: Pending Grace Period Items (if any)
  - Section 1: Due Tomorrow & Next 48 Hours (sorted chronologically)
  - Section 2: Recently Completed Work (submitted within past 24 hours)
- **FR-005**: System MUST dispatch the HTML snapshot email via `ResendNotificationRouter` at 7:00 PM on weekdays.
- **FR-006**: System MUST record dispatch events in Firestore collection `homework_snapshots` with daily idempotency keys.

### Key Entities

- **HomeworkSnapshotPayload**: Structure containing `generated_at`, `student_id`, `upcoming_deadlines` (list of `assignment_id`, `title`, `course`, `due_at`, `portal`, `submitted`), `grace_period_items` (list of `assignment_id`, `title`, `course`, `hours_remaining`), and `recently_completed` (list of assignments submitted in past 24 hours).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of weekday 7:00 PM scheduled snapshot runs generate and dispatch an HTML email.
- **SC-002**: All assignments with due dates in the `[now, now + 48 hours]` window are included in the upcoming section.
- **SC-003**: 100% of active `GRACE_PERIOD` items are highlighted in the snapshot callout section.
- **SC-004**: Zero duplicate snapshot emails are dispatched on any given calendar day.
