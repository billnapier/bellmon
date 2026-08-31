# Feature Specification: Phase 1.8 Daily Heartbeat & System Activity Briefing

**Feature Branch**: `016-phase-1-8-daily-heartbeat-briefing`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: Weekday 5:15 PM scheduled briefing email confirming ingestion status, active grace period timers, period attendance summary, positive zero-alert standing, and alert ledger tracking (CUJ-9)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Ingestion Proof & Heartbeat Confirmation (Priority: P1)

As a parent, I want to receive a daily 5:15 PM email confirming that the system successfully synced data from Canvas and PowerSchool so that I have peace of mind that monitoring is active and working without silent failures.

**Why this priority**: Eliminates user anxiety regarding background monitoring status and provides visible proof of daily operation.

**Independent Test**: Triggering the heartbeat generator with successful ingestion timestamps produces an HTML email displaying green status indicators for Canvas API and PowerSchool scraper.

**Acceptance Scenarios**:

1. **Given** daily ingestion completed successfully at 5:00 PM, **When** the 5:15 PM heartbeat trigger executes, **Then** an HTML email briefing is generated containing the sync execution timestamp and portal health indicators (`Canvas API: OPERATIONAL`, `PowerSchool Portal: OPERATIONAL`).
2. **Given** an ingestion error or partial portal failure during the 5:00 PM sync, **When** the heartbeat executes, **Then** the status banner highlights the affected portal status in yellow/red with error diagnostic details.

---

### User Story 2 - Active Grace Period Watchlist & Hours Remaining (Priority: P1)

As a parent, I want the daily briefing to list all assignments currently buffering in the 36-hour grace period with their remaining hours so that I can see pending items before they escalate to P0 parent alerts.

**Why this priority**: Gives parents early visibility into buffering assignments without triggering premature missing work alarms.

**Independent Test**: Evaluating a student with 1 active grace period assignment (14 hours remaining) includes a dedicated Watchlist card showing assignment name, course, due date, and hours remaining.

**Acceptance Scenarios**:

1. **Given** 1 or more assignments in state `GRACE_PERIOD` in Firestore, **When** the briefing is rendered, **Then** a "Grace Period Watchlist" section lists each assignment, course, original due date, and calculated remaining grace hours.
2. **Given** 0 assignments in grace period, **When** the briefing is rendered, **Then** the watchlist section displays "No active grace period items. All digital work submitted."

---

### User Story 3 - Daily Attendance & Zero-Alert Standing (Priority: P1)

As a parent, I want the briefing to summarize today's period attendance and confirm that zero high-priority grade drops or absences occurred so that positive performance is acknowledged.

**Why this priority**: Reassures parents when everything is on track and reinforces consistent daily attendance.

**Independent Test**: Executing the briefing renderer on a day with 6 present periods and zero grade drop alerts displays "6/6 Periods Present" and a green "Zero Alerts Triggered Today" sentinel badge.

**Acceptance Scenarios**:

1. **Given** period attendance records for the current date in Firestore, **When** evaluated, **Then** the briefing displays a period-by-period breakdown (e.g. `Period 1: Present`, `Period 2: Present`, etc.) and total count summary.
2. **Given** zero P0 alerts (CUJ-1, CUJ-2, CUJ-4, CUJ-5) dispatched during today's ingestion run, **When** evaluated, **Then** the email displays a positive confirmation badge ("Sentinel Standing: Operational — 0 Critical Alerts Dispatched Today").

---

### Edge Cases

- What if the 5:00 PM ingestion job has not run yet or failed completely before 5:15 PM?
  - The heartbeat job detects missing ingestion logs and sends an alert-styled heartbeat indicating ingestion delay.
- What happens on weekends (Saturday/Sunday)?
  - Heartbeat scheduler executes on weekdays only (Monday through Friday).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `HeartbeatBriefingGenerator` in `src/notifications/heartbeat.py`.
- **FR-002**: System MUST query Firestore for daily ingestion execution logs, active `GRACE_PERIOD` records, today's `attendance_records`, and today's alert ledger dispatches.
- **FR-003**: System MUST calculate exact remaining grace hours for active watchlist items using weekday 8:00 AM - 5:00 PM business hour rules.
- **FR-004**: System MUST render an HTML email template containing Ingestion Health, Grace Period Watchlist, Daily Attendance Summary, and Sentinel Standing.
- **FR-005**: System MUST dispatch the email briefing via `ResendNotificationRouter` at 5:15 PM on weekdays.
- **FR-006**: System MUST record heartbeat dispatch events in the Firestore alert ledger (`heartbeat_briefings` collection) to ensure idempotency.

### Key Entities

- **HeartbeatPayload**: Structure containing `sync_timestamp`, `canvas_status`, `powerschool_status`, `grace_watchlist` (list of `assignment_id`, `course`, `title`, `hours_remaining`), `attendance_summary` (`total_periods`, `present_count`, `period_details`), and `zero_alert_confirmed` (boolean).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of weekday 5:15 PM scheduled runs generate and dispatch a valid HTML heartbeat briefing.
- **SC-002**: Grace period watchlist accurately calculates remaining hours within $\pm 5$ minutes accuracy.
- **SC-003**: Daily attendance breakdown accurately reflects period records stored during the 5:00 PM ingestion sync.
- **SC-004**: All heartbeat dispatches are recorded in Firestore to prevent duplicate daily emails.
