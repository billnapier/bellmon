# Feature Specification: Phase 2.2 Sunday Evening Weekly Planning Digest

**Feature Branch**: `012-phase-2-2-sunday-planning-digest`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: Sunday 6:00 PM HTML & Plaintext weekly planning digest consolidating course grade standings, 7-day upcoming deadline timeline, Workload Clumping Radar warning banners, and weekly tardy/unverified attendance summaries (PRD §4.4, CUJ-6)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consolidated Weekly HTML & Plaintext Digest Rendering (Priority: P0)

As a parent, I want to receive a comprehensive Sunday evening email digest consolidating my child's current grades, 7-day upcoming deadlines, workload clumping warnings, and attendance tardies into a single structured report so that our family can prepare for the week ahead.

**Why this priority**: Eliminates Sunday-night surprises and provides a single weekly planning summary.

**Independent Test**: Executing `SundayDigestRenderer.render()` with sample grade, assignment, radar result, and attendance data returns validated HTML and plaintext strings containing all four required sections.

**Acceptance Scenarios**:

1. **Given** active course grades, upcoming assignments, workload radar results, and weekly attendance records, **When** `SundayDigestRenderer.render()` is invoked, **Then** an HTML body and plain text string are generated containing:
   - Section 1: Workload Clumping Radar Banner (if active)
   - Section 2: Current Grade Standings table (course, letter grade, percentage, teacher)
   - Section 3: 7-Day Deadline Timeline (sorted chronologically)
   - Section 4: Weekly Attendance & Tardy Summary (`T` tardies and `U` unverified absences)
2. **Given** no workload clumping is detected (`has_clumping == False`), **When** rendered, **Then** the workload warning banner section is omitted or displays a clean status indicator.

---

### User Story 2 - Resend Email Dispatch & Sunday Schedule Trigger (Priority: P0)

As a system operator, I want the Sunday digest triggered automatically at 6:00 PM on Sundays and delivered via Resend to parent email addresses so that digest delivery is hands-free and timely.

**Why this priority**: Core delivery mechanism for the weekly digest feature.

**Independent Test**: Invoking `SundayDigestRouter.dispatch_if_due()` on a Sunday at 6:00 PM dispatches the email via `ResendNotificationRouter` and records a dispatch entry in Firestore.

**Acceptance Scenarios**:

1. **Given** execution time is Sunday between 5:45 PM and 6:15 PM, **When** `SundayDigestRouter.dispatch_if_due()` is called, **Then** the rendered digest is sent via `ResendNotificationRouter`.
2. **Given** execution time is a weekday, **When** `SundayDigestRouter.dispatch_if_due()` is called, **Then** dispatch is skipped.

---

### User Story 3 - Firestore Deduplication & Idempotency (Priority: P1)

As a parent, I want digest dispatches tracked in Firestore so that I never receive duplicate digest emails on the same Sunday.

**Why this priority**: Prevents duplicate emails if the scheduled batch job retries or executes multiple times during the Sunday window.

**Independent Test**: Triggering `SundayDigestRouter.dispatch_if_due()` twice on the same Sunday results in 1 email dispatch and records key `digest_last_sent_at` in Firestore.

**Acceptance Scenarios**:

1. **Given** a successful digest dispatch on `2026-09-06`, **When** recorded in Firestore, **Then** `digest_last_sent_at` is set to `2026-09-06T18:00:00Z`.
2. **Given** `digest_last_sent_at` is already set for the current Sunday, **When** executed again, **Then** dispatch is skipped.

---

### Edge Cases

- What if a course has no numerical grade or percentage available yet?
  - Display letter grade or "N/A" with current status note without breaking HTML table formatting.
- What if there are zero upcoming assignments due in the next 7 days?
  - Section 3 displays "No upcoming deadlines scheduled for the next 7 days."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `SundayDigestRenderer` in `src/digest/renderer.py`.
- **FR-002**: System MUST implement `SundayDigestRouter` in `src/digest/router.py`.
- **FR-003**: System MUST format a responsive HTML email containing:
  - Header: "Bellmon Weekly Planning Digest" with student name and timestamp
  - Section 1: Workload Clumping Radar Warning (when `has_clumping == True`)
  - Section 2: Current Grade Standings Table
  - Section 3: 7-Day Deadline Timeline
  - Section 4: Weekly Attendance & Tardy Summary
- **FR-004**: System MUST produce a matching plain text alternative string for non-HTML email clients.
- **FR-005**: System MUST record dispatch timestamps in Firestore collection `digest_ledger` to enforce idempotency within a 48-hour window.

### Key Entities

- **SundayDigestPayload**: Structure containing `student_name`, `generated_at`, `courses` (list of course, percentage, letter grade), `deadlines` (list of assignment, course, due date), `radar_result` (`WorkloadRadarResult`), and `attendance_summary` (tardy and unverified counts).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Sunday 6:00 PM batch runs generate and dispatch both HTML and plaintext digest emails.
- **SC-002**: Workload clumping banners render dynamically whenever `has_clumping == True`.
- **SC-003**: Zero duplicate digest emails are dispatched within any 48-hour window.
