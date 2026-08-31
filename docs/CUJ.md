# Critical User Journeys (CUJs) - Bellmon (Bellarmine Monitor)

This document defines the Critical User Journeys (CUJs) for the Bellmon monitoring system, derived directly from the Product Requirements Document (`Prd.md`) and ratified technical decisions.

---

## Stakeholder Personas & Roles

* **Parent / Guardian**: Primary consumer of push notifications and weekly digests. Desires early warning visibility into academic risks without needing to micromanage or log into portals daily.
* **Student**: Primary subject of monitoring. Requires autonomy, zero-friction self-advocacy windows (grace periods), and protection against false alarms caused by paper submissions or teacher grading delays.
* **Sentinel System (Automated Operator)**: Background engine executing scheduled ingestion, state diffing, heuristic evaluation, and alert routing.

---

## Core CUJ Matrix Summary

| CUJ ID | Name | Priority | Trigger Source | Primary Output | Key Business Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CUJ-1** | Digital Missing Assignment with Grace Period | P0 (Deferred) | Canvas LMS | Email Alert (Post 36h) | 36 calendar hours delay window (pauses weekends) |
| **CUJ-2** | Confirmed PowerSchool Missing Work Alert | P0 | PowerSchool SIS | Immediate Email Alert | Immediate dispatch if score $=0$ or `isMissing: true` |
| **CUJ-3** | Paper / Non-Digital Work Handling | N/A (Internal) | Canvas LMS | Alert Suppressed | Suppress Canvas missing alert for `on_paper` or `none` submission types |
| **CUJ-4** | Significant Grade Trajectory Drop Warning | P0 | PowerSchool SIS | Immediate Email Alert | Alert on rolling velocity drop $\ge 4.0\%$ vs 7-10 day snapshot |
| **CUJ-5** | Attendance Anomaly Detection | P0 | PowerSchool SIS | Daily 5pm Email Alert | Alert on unexcused absence (`A`) or cut (`CUT`) |
| **CUJ-6** | Sunday Night Workload & Planning Digest | P1 | Scheduled (Sun 6pm) | HTML Email Digest | Flag $\ge 2$ major assessments within 48-hour window + Tardy summary |
| **CUJ-7** | Automated Daily Ingestion & State Diff Sync | System | Scheduled Cron | Firestore State Update | Idempotent state diffing and ledger tracking in Cloud Firestore |
| **CUJ-8** | Canvas Late Submission Reporting & Frequency Tracking | P1 | Canvas LMS | Sunday Digest / P1 Warning | Track `late: true` submissions in Canvas; report in Sunday Digest and trigger warning if $\ge 3$ late in 7 days |
| **CUJ-9** | Daily Heartbeat & System Activity Briefing | P1 | Scheduled (Weekdays 5:15pm) | HTML Email Briefing | Delivers daily ingestion proof, active grace period watchlist, attendance summary, and zero-alert confirmation |
| **CUJ-10** | Daily Evening Homework & Deadline Snapshot | P1 | Scheduled (Weekdays 7:00pm) | HTML Email Snapshot | Unified 24-48h upcoming deadline view and pending grace period submission reminders |

---

## Detailed Critical User Journeys

### CUJ-1: Digital Missing Assignment with Grace Period (36 Weekday Hours)
* **Goal**: Give the student a 36-calendar-hour window (pausing weekends) to submit an overdue digital assignment or contact their teacher before notifying parents.
* **Preconditions**:
  * Canvas reports `missing: true` for an assignment with `submission_types = ['online_upload']`.
* **User Workflow**:
  1. System detects missing digital submission during daily 5:00 PM sync.
  2. System records `first_detected_missing` timestamp in Firestore with status `GRACE_PERIOD`.
  3. **Timer Progression (36 Hours)**:
     * Timer pauses at 5:00 PM Friday and resumes at 8:00 AM Monday.
     * If student uploads assignment (Canvas `missing: false`), state updates to `RESOLVED` (no alert).
  4. **After 36 Hours**:
     * If assignment remains missing in Canvas, system elevates state to `ALERT_DISPATCHED`.
     * System dispatches P0 Email Alert: *"Missing Digital Assignment (Post-Grace): [Assignment Name] in [Course] (Due: [Date])"*.

---

### CUJ-2: Confirmed PowerSchool Missing Work Alert
* **Goal**: Promptly alert parents when an assignment is explicitly confirmed as missing in PowerSchool by the teacher.
* **Preconditions**:
  * PowerSchool SIS reports `isMissing: true` OR `score: 0`.
* **User Workflow**:
  1. System ingests latest grades and assignment flags from PowerSchool.
  2. Engine identifies explicit missing flag or zero score entered by teacher.
  3. Canvas grace period is bypassed (PowerSchool is official system of record).
  4. System dispatches P0 Email Alert during daily batch (5:00 PM weekdays): *"Confirmed Missing Work: [Assignment Name] in [Course] - 0/[Points] points"*.

---

### CUJ-3: Paper / Non-Digital Work Handling
* **Goal**: Eliminate false missing assignment alarms for physical paper hand-ins or discussion assignments not turned in digitally via Canvas.
* **Preconditions**:
  * Canvas reports `missing: true`.
  * Canvas `submission_types` is NOT `online_upload` (e.g., `on_paper`, `discussion_topic`, `none`).
* **User Workflow**:
  1. System checks Canvas submission type.
  2. Rule engine identifies non-digital delivery method.
  3. System suppresses Canvas alert (`SUPPRESSED_NON_DIGITAL`).
  4. System defers entirely to PowerSchool SIS gradebook reporting.

---

### CUJ-4: Significant Grade Trajectory Drop Warning
* **Goal**: Alert parents to a sudden drop in course performance ($\ge 4.0\%$) compared to the closest snapshot in Firestore within $[t-10, t-7]$ days.
* **Preconditions**:
  * PowerSchool grade history has snapshots in Firestore for at least 7 days.
  * Course has $\ge 100$ total graded points OR current term length is $\ge 21$ calendar days (eliminates early-term noise).
* **User Workflow**:
  1. System calculates percentage drop: $\Delta = \text{Grade}_{t-\text{prev}} - \text{Grade}_{\text{current}}$.
  2. If $\Delta \ge 4.0\%$ AND minimum denominator precondition is met:
     * System dispatches P0 Email Alert: *"Grade Drop Alert: [Course] dropped from [Old Grade]% to [New Grade]% (-[Delta]%)"*.

---

### CUJ-5: Attendance Anomaly Processing (Tiered Severity)
* **Goal**: Immediately alert parents on unexcused absences or cuts during the daily 5:00 PM batch run while batching minor tardies into the Sunday digest.
* **Preconditions**:
  * PowerSchool period attendance records updated during daily sync.
* **User Workflow**:
  1. System inspects daily attendance entries per class period.
  2. Ignores standard present/excused codes (`P`, `E`, `EX`, `ACT`).
  3. **High-Severity Path (`A` Unexcused Absence or `CUT` Class Cut)**:
     * Checks Firestore ledger to prevent duplicate alerts for the same period date.
     * System dispatches P0 Email Alert at 5:00 PM weekdays: *"Attendance Alert: Period [P#] ([Course]) marked as [Code Description] on [Date]"*.
  4. **Low-Severity Path (`T` Tardy or `U` Unverified)**:
     * Logs event in Firestore state store under `attendance_events`.
     * Queues record for inclusion in CUJ-6 Sunday Night Planning Digest.

---

### CUJ-6: Sunday Night Workload & Planning Digest
* **Goal**: Provide parent and student with a weekly overview of course standings and a forward-looking radar for heavy test/project clusters.
* **Preconditions**:
  * Sunday 6:00 PM scheduled trigger.
* **User Workflow**:
  1. System gathers current grade summary across all enrolled courses from Firestore.
  2. System analyzes upcoming 7-day calendar deadlines from Canvas and PowerSchool.
  3. System checks for **Workload Clumping**: $\ge 2$ major assessments (category matching `Exam`, `Test`, `Project`, `Midterm` or `points >= 50`) due within any 48-hour window.
  4. System builds HTML Email Digest containing:
     * Overall Course Grade Summary.
     * 7-Day Deadline Timeline.
     * High-priority **Workload Clumping Warning Banner** (if triggered).
  5. Router sends HTML email to registered parent/student email address.

---

### CUJ-7: Automated Daily Ingestion & State Diff Sync
* **Goal**: Maintain an up-to-date Cloud Firestore cache of student performance and alert history without requiring user logins or app check-ins.
* **Preconditions**:
  * Scheduled execution (Weekdays at 5:00 PM / Sunday at 6:00 PM).
* **User Workflow**:
  1. Ephemeral Cloud Run Job connects to Canvas API and PowerSchool via Playwright (reusing cookies from Firestore).
  2. Fetches active courses, current percentage, assignment lists, and period attendance.
  3. Compares incoming payload against Google Cloud Firestore state store.
  4. Updates course grade history snapshots.
  5. Runs CUJ-1 through CUJ-6 rule evaluators.
  6. Records all dispatched email notifications in the Firestore alert ledger for idempotency.

---

### CUJ-8: Canvas Late Submission Reporting & Frequency Tracking
* **Goal**: Provide visibility into assignments turned in late on Canvas (which are not flagged as late or missing in PowerSchool), helping parents monitor submission habit trends without false missing alarms.
* **Preconditions**:
  * Canvas submission record contains `late: true` OR `submitted_at > due_at`.
* **User Workflow**:
  1. System detects late digital submission during daily Canvas sync (`/api/v1/users/{id}/courses/{course_id}/assignments` or `/api/v1/students/submissions`).
  2. System logs event in Firestore state store under `late_submissions` with assignment details (`title`, `course`, `due_at`, `submitted_at`, `minutes_late`).
  3. **Sunday Digest Integration (Routine Summary)**:
     * Includes a dedicated section in the CUJ-6 Sunday Night Digest listing all assignments submitted late during the preceding week.
  4. **Frequency Threshold Warning (Optional P1 Trigger)**:
     * If $\ge 3$ assignments are submitted late within any rolling 7-calendar-day window:
     * System dispatches P1 Email Alert: *"Late Submission Pattern Warning: [Count] assignments submitted late in the past 7 days"*.

---

### CUJ-9: Daily Heartbeat & System Activity Briefing
* **Goal**: Eliminate "silent failure" uncertainty by delivering a weekday 5:15 PM briefing that confirms successful data ingestion, active grace period timers, attendance checks, and overall sentinel standing.
* **Preconditions**:
  * Daily 5:00 PM ingestion job execution completes successfully.
* **User Workflow**:
  1. System verifies data ingestion status (`SUCCESS` for Canvas API and PowerSchool scraper).
  2. System queries Firestore for:
     * Active `GRACE_PERIOD` items (with calculated hours remaining before parent alert elevation).
     * Period attendance entries for the current day.
     * Active grade velocity standings across all courses.
  3. System builds and dispatches the HTML Daily Heartbeat Briefing email:
     * **Ingestion Status**: Sync timestamp and portal status indicators.
     * **Grace Period Watchlist**: Active assignments buffering with remaining hours before P0 escalation.
     * **Daily Attendance Result**: Period-by-period attendance log for today (e.g., 6/6 Periods Present).
     * **Sentinel Standings**: Positive confirmation that zero P0 grade drops or unexcused absences were detected today.
  4. Log dispatch record in Firestore alert ledger.

---

### CUJ-10: Daily Evening Homework & Deadline Snapshot
* **Goal**: Provide parent and student with a focused, actionable 7:00 PM briefing of assignments due within the next 24–48 hours across Canvas and PowerSchool.
* **Preconditions**:
  * Weekday 7:00 PM scheduled trigger.
* **User Workflow**:
  1. System queries Firestore for upcoming assignments due within $[t, t+48\text{ hours}]$.
  2. System cross-references active grace period items needing immediate student action/submission.
  3. System builds HTML Email Snapshot containing:
     * **Due Tomorrow & Next 48 Hours**: Formatted list of upcoming assignments by course, due date, and submission type.
     * **Pending Submissions Reminder**: Warning for any digital assignment currently in grace period that must be turned in to avoid parent alert.
  4. System dispatches HTML email to parent and student email addresses.

