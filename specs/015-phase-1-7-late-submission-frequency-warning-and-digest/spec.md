# Feature Specification: Phase 1.7 Late Submission Frequency Warning & Digest Integration

**Feature Branch**: `015-phase-1-7-late-submission-frequency-warning-and-digest`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: Rolling 7-day late submission frequency sentinel ($\ge 3$ late assignments), P1 pattern warning email alert generation, and Sunday Digest integration for CUJ-8

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Late Submission Frequency Pattern Warning (Priority: P1)

As a parent, I want to receive a P1 warning alert when my student submits 3 or more assignments late within a rolling 7-day period so that I am alerted to developing habit patterns before grades suffer.

**Why this priority**: High late submission frequency indicates time-management or workload issues requiring proactive discussion.

**Independent Test**: Simulating 3 late submissions within the past 7 days generates a `PendingLateSubmissionPatternAlert` P1 warning payload.

**Acceptance Scenarios**:

1. **Given** 3 or more late submissions recorded in Firestore within a rolling 7-calendar-day window `[now - 7 days, now]`, **When** evaluated, **Then** engine generates a P1 warning alert payload listing the count, course breakdown, and assignment details.
2. **Given** fewer than 3 late submissions in the rolling 7-day window, **When** evaluated, **Then** no frequency warning alert is generated.

---

### User Story 2 - Frequency Alert Cooldown & Ledger Tracking (Priority: P1)

As a parent, I want to receive at most one late frequency warning per 7-day window so that I am not flooded with warning emails every day while the count remains above threshold.

**Why this priority**: Avoids notification fatigue while keeping alerts actionable.

**Independent Test**: Evaluating a student with 4 late submissions who already received a frequency warning 2 days ago produces 0 new warning alerts.

**Acceptance Scenarios**:

1. **Given** a late frequency warning alert dispatched for `student_id` within the past 7 days recorded in the alert ledger, **When** evaluated again, **Then** duplicate alert dispatch is suppressed until the 7-day cooldown expires.

---

### User Story 3 - Sunday Planning Digest Integration (Priority: P2)

As a parent, I want all assignments submitted late during the preceding week to be summarized in the Sunday Night Digest (CUJ-6) so that I have a consolidated view during weekly planning.

**Why this priority**: Provides routine weekly reporting without needing daily interruption for isolated late submissions.

**Independent Test**: Generating Sunday Digest payload with 2 late submissions from the past week includes a dedicated "Late Submissions This Week" section in the HTML email.

**Acceptance Scenarios**:

1. **Given** late submission records in Firestore dated within the past 7 days, **When** the Sunday Digest renderer executes, **Then** a dedicated HTML table section listing late assignments (title, course, due date, submission date, minutes late) is included in the digest.
2. **Given** 0 late submissions in the past 7 days, **When** the Sunday Digest renderer executes, **Then** the section displays "No late submissions recorded this week."

---

### Edge Cases

- What happens if a late submission occurs on Sunday right before the 6:00 PM digest run?
  - It is included in the Sunday digest section for that week.
- What happens if an assignment is flagged late but turned in only 2 minutes late (e.g. minor clock skew)?
  - A configurable threshold `min_minutes_late` (default: 5 minutes) ignores minor grace period clock skews from triggering frequency alerts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `LateSubmissionSentinel` in `src/engine/late_submissions.py`.
- **FR-002**: System MUST query Firestore `late_submissions` for events in the rolling 7-day window `[now - 7 days, now]`.
- **FR-003**: System MUST filter out late submissions with `minutes_late < min_minutes_late` (default: 5 minutes).
- **FR-004**: System MUST trigger a P1 Warning Alert (`LateSubmissionPatternAlert`) when matching late count is $\ge 3$.
- **FR-005**: System MUST record dispatched frequency warnings in Firestore alert ledger with a 7-day cooldown window.
- **FR-006**: System MUST format late submission data into the Sunday Digest (CUJ-6) HTML template (`src/notifications/digest.py`).

### Key Entities

- **LateSubmissionPatternAlert**: Structure containing `student_id`, `late_count`, `window_start`, `window_end`, `late_assignments_summary`, and `detected_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of rolling 7-day windows with $\ge 3$ qualifying late submissions generate a P1 warning alert payload on first occurrence.
- **SC-002**: Zero duplicate frequency warnings are dispatched during the 7-day cooldown period.
- **SC-003**: The Sunday Digest includes 100% of late submissions recorded during the preceding week.
