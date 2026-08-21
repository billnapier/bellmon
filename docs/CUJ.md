# Critical User Journeys (CUJs) - Bellmon: Student Academic & Workload Sentinel

This document defines the Critical User Journeys (CUJs) for the Bellmon monitoring system, derived directly from the Product Requirements Document (`Bellmon_PRD.md`).

---

## Stakeholder Personas & Roles

* **Parent / Guardian**: Primary consumer of push notifications and weekly digests. Desires early warning visibility into academic risks without needing to micromanage or log into portals daily.
* **Student**: Primary subject of monitoring. Requires autonomy, zero-friction self-advocacy windows (grace periods), and protection against false alarms caused by paper submissions or teacher grading delays.
* **Sentinel System (Automated Operator)**: Background engine executing scheduled ingestion, state diffing, heuristic evaluation, and alert routing.

---

## Core CUJ Matrix Summary

| CUJ ID | Name | Priority | Trigger Source | Primary Output | Key Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CUJ-1** | Digital Missing Assignment with Grace Period | P0 (Deferred) | Canvas | Push Alert (Post 36h) | 36-hour delay window for student self-correction |
| **CUJ-2** | Confirmed Missing Work Alert | P0 | Canvas & PowerSchool | Immediate Push Alert | Immediate dispatch if score $=0$ or `isMissing: true` |
| **CUJ-3** | Paper / In-Class Work False-Positive Suppression | N/A (Internal) | Canvas & PowerSchool | Alert Suppressed | Suppress alert if PowerSchool score $>0$ or `isCollected: true` |
| **CUJ-4** | Significant Grade Trajectory Drop Warning | P0 | PowerSchool | Immediate Push Alert | Alert on rolling 7-day velocity drop $\ge 4.0\%$ |
| **CUJ-5** | Attendance Anomaly Detection | P0 | PowerSchool | Real-time / Daily Push | Alert on unexcused absence, tardy, or cut |
| **CUJ-6** | Sunday Night Workload & Planning Digest | P1 | Scheduled (Sun 6pm) | HTML Email Digest | Flag $\ge 2$ major assessments within 48-hour window |
| **CUJ-7** | Automated Daily Ingestion & State Diff Sync | System | Scheduled Cron | Updated State Store | Idempotent state diffing and ledger tracking |

---

## Detailed Critical User Journeys

### CUJ-1: Digital Missing Assignment with Grace Period
* **Goal**: Give the student a 36-hour window to submit an overdue digital assignment or contact their teacher before notifying parents.
* **Preconditions**:
  * Canvas reports `missing: true` for an assignment with `submission_types = ['online_upload']`.
  * PowerSchool shows no score entered (`-`) and `isMissing` is false.
* **User Workflow**:
  1. System detects missing digital submission during daily sync.
  2. System records `first_detected_missing` timestamp in state store with status `GRACE_PERIOD`.
  3. **Within 36 hours**:
     * If student uploads assignment (Canvas `missing: false`), state updates to `RESOLVED` (no alert).
     * If teacher grades assignment in PowerSchool (score $>0$), state updates to `SUPPRESSED` (no alert).
  4. **After 36 hours**:
     * If assignment remains missing and unrecorded, system elevates state to `ALERT_DISPATCHED`.
     * System fires P0 Push Alert: *"Missing Digital Assignment (Post-Grace): [Assignment Name] in [Course] (Due: [Date])"*.

---

### CUJ-2: Confirmed Missing Work Alert
* **Goal**: Promptly alert parents when an assignment is explicitly confirmed as missing by the teacher or missing across both systems.
* **Preconditions**:
  * Canvas `missing: true` AND PowerSchool `isMissing: true` (or `score: 0`), **OR**
  * Canvas `missing: false` AND PowerSchool `isMissing: true` (or `score: 0`).
* **User Workflow**:
  1. System ingests latest grades and assignment flags.
  2. Rule engine identifies explicit missing confirmation in PowerSchool.
  3. Grace period is bypassed.
  4. System dispatches P0 Push Alert during daily batch (5:00 PM): *"Confirmed Missing Work: [Assignment Name] in [Course] - 0/[Points] points"*.

---

### CUJ-3: Paper / In-Class Work False-Positive Suppression
* **Goal**: Eliminate false missing assignment alarms caused by physical paper hand-ins or discussion assignments not turned in via Canvas.
* **Preconditions**:
  * Canvas reports `missing: true`.
  * PowerSchool reports `score > 0` OR `isCollected: true`.
* **User Workflow**:
  1. System correlates Canvas assignment with PowerSchool gradebook item.
  2. Rule engine detects that PowerSchool confirms physical collection or recorded points.
  3. System logs `SUPPRESSED_PAPER_OR_GRADED` in state store.
  4. No notification is generated.

---

### CUJ-4: Significant Grade Trajectory Drop Warning
* **Goal**: Alert parents to a sudden drop in course performance ($\ge 4.0\%$) over a 7-day period so support can be provided early.
* **Preconditions**:
  * PowerSchool grade history has snapshots for at least 7 days.
* **User Workflow**:
  1. System calculates 7-day percentage change: $\Delta = \text{Grade}_{t-7} - \text{Grade}_{current}$.
  2. If $\Delta \ge 4.0\%$:
     * System identifies new assignment(s) entered within that 7-day window.
     * System isolates the assignment responsible for the maximum point loss.
  3. System dispatches P0 Push Alert: *"Grade Drop Alert: [Course] dropped from [Old Grade]% to [New Grade]% (-[Delta]%). Impacting item: [Assignment Title] ([Score]/[Points])"*.

---

### CUJ-5: Attendance Anomaly Detection
* **Goal**: Provide visibility into unexcused period absences, tardies, or cuts on the day they occur.
* **Preconditions**:
  * PowerSchool period attendance records updated.
* **User Workflow**:
  1. System inspects daily attendance entries per class period.
  2. Ignores standard present/excused codes (`P`, `E`, `EX`, `ACT`).
  3. Matches codes $\in \{\text{'A' (Unexcused)}, \text{'T' (Tardy)}, \text{'U' (Unverified)}, \text{'CUT'}\}$.
  4. Checks ledger to prevent duplicate alerts for the same period date.
  5. System dispatches P0 Push Alert (4:00 PM or real-time): *"Attendance Alert: Period [P#] ([Course]) marked as [Code Description] on [Date]"*.

---

### CUJ-6: Sunday Night Workload & Planning Digest
* **Goal**: Provide parent and student with a weekly overview of course standings and a forward-looking radar for heavy test/project clusters.
* **Preconditions**:
  * Sunday 6:00 PM scheduled trigger.
* **User Workflow**:
  1. System gathers current grade summary across all enrolled courses.
  2. System analyzes upcoming 7-day calendar deadlines from Canvas and PowerSchool.
  3. System checks for **Workload Clumping**: $\ge 2$ major assessments (category matching `Exam`, `Test`, `Project`, `Midterm` or `points >= 50`) due within any 48-hour window.
  4. System builds HTML Email Digest containing:
     * Overall Course Grade Summary.
     * 7-Day Deadline Timeline.
     * High-priority **Workload Clumping Warning Banner** (if triggered).
  5. Router sends HTML email to registered parent/student email address.

---

### CUJ-7: Automated Daily Ingestion & State Diff Sync
* **Goal**: Maintain an up-to-date local cache of student performance and alert history without requiring user logins or app check-ins.
* **Preconditions**:
  * Scheduled execution (Daily at 5:00 PM / Sunday at 6:00 PM).
* **User Workflow**:
  1. Engine connects to Canvas API and PowerSchool Parent API.
  2. Fetches active courses, current percentage, assignment lists, and period attendance.
  3. Compares incoming payload against local SQLite state store.
  4. Updates course grade history snapshots.
  5. Runs CUJ-1 through CUJ-6 rule evaluators.
  6. Records all dispatched notifications in the alert ledger for idempotency.
