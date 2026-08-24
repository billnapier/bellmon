# Feature Specification: Phase 1.4 Period Attendance Anomaly Sentinel (P0 Alerting)

**Feature Branch**: `009-phase-1-4-attendance-anomaly-sentinel`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Phase 1.4 Period-level attendance anomaly evaluation, P0 unexcused absence/cut alerting, and alert deduplication ledger

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Period Unexcused Absence & Class Cut P0 Detection (Priority: P1)

As a parent, I want immediate P0 email alerts on weekdays when an unexcused absence (`A`) or class cut (`CUT`) is recorded for any specific period in PowerSchool so that attendance anomalies are addressed on the day they occur.

**Why this priority**: Unexcused absences and class cuts represent urgent behavioral risk factors that require timely intervention.

**Independent Test**: Feeding a PowerSchool attendance record with code `A` or `CUT` for Period 2 Algebra produces a `PendingAttendanceAlert`.

**Acceptance Scenarios**:

1. **Given** a PowerSchool period attendance record with code `A` (Unexcused Absence) or `CUT` (Class Cut), **When** evaluated, **Then** engine creates a pending P0 attendance alert payload.
2. **Given** an attendance code of `P` (Present), `E` / `EX` (Excused Absence), or `ACT` (School Activity), **When** evaluated, **Then** engine ignores the event and emits zero alerts.

---

### User Story 2 - Attendance Alert Deduplication (Priority: P1)

As a parent, I want to receive exactly one alert per unexcused absence or cut event so that I am not spammed with duplicate emails on subsequent sub-daily sync runs.

**Why this priority**: Avoids repetitive email alerts for the same historical attendance record.

**Independent Test**: Evaluating an attendance event `(date: "2026-08-21", period: 1)` already recorded in Firestore with `notified: true` yields no new alert.

**Acceptance Scenarios**:

1. **Given** an attendance event matching `(date, period, course)` already present in Firestore `attendance_events` with `notified: true`, **When** re-evaluated on subsequent runs, **Then** duplicate alert generation is suppressed.

---

### User Story 3 - Minor Attendance Code Queuing for Sunday Digest (Priority: P2)

As a parent, I want minor attendance codes like tardies (`T`) or unverified entries (`U`) recorded in Firestore without triggering P0 immediate email alerts so that minor events are summarized in the Sunday digest instead of interrupting my workday.

**Why this priority**: Eliminates noise from minor tardies while preserving data for weekly summary reports.

**Independent Test**: Evaluating attendance code `T` adds the event to `attendance_events` with `notified: false` but emits no immediate P0 alert payload.

**Acceptance Scenarios**:

1. **Given** an attendance record with code `T` (Tardy) or `U` (Unverified), **When** evaluated, **Then** the event is logged to Firestore `attendance_events` with `notified: false` and zero immediate P0 alerts are queued.

---

### Edge Cases

- What happens if an unexcused absence code `A` is later updated by the school office to excused `E`?
  - The attendance event entry in Firestore reflects the code change; no retrospective withdrawal email is sent, but future alert evaluation sees code `E` and ignores it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `AttendanceSentinel` in `src/engine/attendance.py`.
- **FR-002**: System MUST parse period-level attendance records harvested from PowerSchool SIS.
- **FR-003**: System MUST categorize attendance codes into P0 Urgent (`A`, `CUT`), P1 Digest (`T`, `U`), or Ignored (`P`, `E`, `EX`, `ACT`).
- **FR-004**: System MUST check Firestore `attendance_events` array for existing records matching `(date, period, course)`.
- **FR-005**: System MUST generate `PendingAttendanceAlert` records for un-notified P0 events.
- **FR-006**: System MUST persist new attendance records into Firestore `attendance_events` with `notified` status flags.

### Key Entities

- **AttendanceCodeSeverity**: Enum (`P0_URGENT`, `P1_DIGEST`, `IGNORED`).
- **PendingAttendanceAlert**: Structure containing `date`, `period`, `course_name`, `code`, `description`, and `detected_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of period unexcused absences (`A`) and class cuts (`CUT`) generate P0 alert payloads on first detection.
- **SC-002**: Zero duplicate notifications are dispatched for previously notified attendance events.
- **SC-003**: Excused absences (`E`, `EX`) and present codes (`P`) produce zero alert payloads.
