# Product Definition: Bellarmine Monitor (Bellmon)

## 1. Executive Summary & Goals

### 1.1 Overview
The **Student Academic & Workload Sentinel** is an automated, event-driven monitoring pipeline engineered to ingest academic, assignment, and attendance data from **Canvas LMS** and **PowerSchool SIS**. 

The system provides early-warning visibility into student risk factors—specifically unsubmitted assignments, steep grade trajectory drops, attendance anomalies, and high-stakes workload clumping—while strictly preserving student autonomy through heuristic-based noise filtering, configurable grace periods, and zero required app check-ins.

### 1.2 Core Objectives
* **Zero-Touch Monitoring:** Deliver all actionable insights directly to parents/guardians via structured, responsive HTML email notifications (SendGrid / SMTP); eliminate manual portal logins and app-checking.
* **Noise & False-Positive Elimination:** Use an Asymmetric System Authority Model to decouple Canvas digital submissions from PowerSchool official gradebook records, eliminating paper submission mismatches and grading lag artifacts.
* **Proactive Trajectory Tracking:** Alert on grade velocity drops ($\Delta \ge 4.0\%$) and upcoming workload clustering rather than waiting for formal report cards or end-of-term deficits.
* **Student Autonomy & Grace Periods:** Provide a 36-hour delay window (1.5 calendar days, pausing on weekends) before emailing parents about digital missing assignments in Canvas, empowering students to self-advocate and resolve discrepancies with teachers directly.

---

## 2. System Architecture

```
 ┌──────────────────────┐        ┌──────────────────────┐
 │      Canvas LMS      │        │    PowerSchool SIS   │
 │   - REST API         │        │   - Playwright SAML  │
 └──────────┬───────────┘        └──────────┬───────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       Cloud Run Job           │
            │   (Daily Cron / Serverless)   │
            │   - Fetch latest state        │
            │   - Evaluate system authority │
            │   - Compute state diffs       │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │   Google Cloud Firestore      │
            │   - Assignment status cache   │
            │   - Grade trajectory history  │
            │   - Alert dispatch ledger     │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       Alert Rules Engine      │
            │   - Grace period verification │
            │   - Delta threshold checks    │
            │   - Workload clumping analysis│
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Notification Router      │
            ├───────────────┬───────────────┤
            │ P0: Urgent    │ P1: Digest    │
            │ Email (5 PM)  │ Email (Sun)   │
            └───────────────┴───────────────┘
```

---

## 3. Data Ingestion & Integration Layer

### 3.1 Canvas LMS Ingestion
Canvas serves as the primary system for digital assignments, project descriptions, upcoming due dates, and learning materials.

* **API Endpoints:**
  * `GET /api/v1/users/:observee_id/missing_submissions`: Retrieves overdue assignments lacking a submission record.
  * `GET /api/v1/courses/:course_id/assignments`: Fetches complete course assignment structures, category weightings, and rubric details.
  * `GET /api/v1/calendar_events`: Ingests forward-looking calendar entries for exam and deadline radar tracking.
* **Extracted Attributes:**
  * `assignment_id` (Integer)
  * `course_id` (Integer)
  * `name` (String)
  * `due_at` (ISO8601 Timestamp)
  * `submission_types` (Array: `['online_upload']`, `['on_paper']`, `['none']`, `['discussion_topic']`)
  * `points_possible` (Float)
  * `has_submitted_submissions` (Boolean)

### 3.2 PowerSchool SIS Ingestion
PowerSchool serves as the official district gradebook of record and master attendance ledger.

* **Mechanism:** Playwright Chromium headless browser session.
  * Attempts session cookie reuse from Firestore first; falls back to SAML SSO login with credentials from Secret Manager.
* **Extracted Attributes:**
  * `course_name` (String)
  * `current_percentage` (Float)
  * `letter_grade` (String: e.g., 'A-', 'B+')
  * `teacher_name` (String)
  * `period_attendance` (Array of objects: `{ date, period, code, description }`)
  * `assignment_records` (Array of objects with status flags: `isMissing`, `isLate`, `score`, `pointsPossible`)

---

## 4. Heuristic & Business Logic Engine

### 4.1 Decoupled Ingestion & Asymmetric System Authority Model
Bellmon operates on a strict **Asymmetric System Authority Model**. Canvas LMS and PowerSchool SIS entities are tracked independently; no cross-system title or due-date matching algorithm is performed.

#### System Authority Roles:
* **Canvas LMS Authority:** Sole authority for digital submissions (`submission_types: ['online_upload']`). If Canvas reports `missing: true`, a 36-calendar-hour grace period is initiated.
* **PowerSchool SIS Authority:** Sole authority for official teacher gradebook records, physical paper hand-ins, and attendance. If PowerSchool flags `isMissing: true` or `score: 0`, an immediate P0 email alert is triggered.

#### Grace Period Definition (36 Elapsed Hours):
* The 36-hour grace period runs continuously during weekdays and **pauses on weekends** (Friday at 5:00 PM to Monday at 8:00 AM).
* Official school holiday calendars are excluded from runtime logic to maintain low system complexity.
* *Example:* An assignment due Monday at 11:59 PM initiates the timer on Tuesday at 12:00 AM. If still unsubmitted, an alert triggers Wednesday at 12:00 PM (36 elapsed weekday hours).

#### Missing Work Resolution Matrix

| Ingestion Source | Observed System Flag | Reality / Root Cause | Engine Action |
| :--- | :--- | :--- | :--- |
| **Canvas LMS** | `missing: true` (`online_upload`) | Unsubmitted digital work or pending teacher update | **Initiate 36-Hour Grace Period**. Pause timer on weekends. |
| **PowerSchool SIS** | `isMissing: true` or `score: 0` | Teacher explicitly recorded missing work in SIS | **Fire P0 Email Alert** immediately during 5:00 PM daily batch sync. |
| **Canvas LMS** | `missing: true` (`on_paper` / `none`) | Physical assignment not submitted via Canvas | **Suppress Canvas alert**. Rely solely on PowerSchool SIS gradebook updates. |


### 4.2 Grade Trajectory & Velocity Drop Detection
To eliminate false alarms caused by early-term grade volatility, velocity drops are evaluated with a minimum point / term threshold.

* **Mathematical Trigger:**
  $$\Delta = \text{Grade}_{t-\text{prev}} - \text{Grade}_{t-\text{curr}} \ge 4.0\%$$
  Evaluated against the closest historical snapshot in Firestore within a $[t-10, t-7]$ day window per course. Velocity drop alerts are suppressed until at least 7 days of history accumulate.
* **Minimum Point / Term Threshold (Noise Suppressor):**
  * Velocity drop evaluation is **suppressed** unless the course has **$\ge 100$ total graded points** OR the current term has been active for **$\ge 21$ calendar days** (3 weeks).
* **Payload Structure:** The alert payload includes Course Name, Previous Grade %, Current Grade %, and Delta % ($\Delta$). Specific assignment attribution is omitted to keep the alert simple and unambiguous.

### 4.3 Attendance Anomaly Processing
Attendance anomalies are evaluated using a **Tiered Severity Model** during the daily 5:00 PM batch run.

* **P0 High-Priority Trigger (Daily 5:00 PM Email Alert):**
  * Period codes $\in \{\text{'A' (Unexcused Absence)}, \text{'CUT' (Class Cut)}\}$.
* **P1 Digest Trigger (Sunday Email Digest):**
  * Period codes $\in \{\text{'T' (Tardy)}, \text{'U' (Unverified)}\}$.
* **Suppression Conditions:** Standard present or authorized excused codes ($\{\text{'P' (Present)}, \text{'E' (Excused)}, \text{'EX'}, \text{'ACT' (School Activity)}\}$) are ignored.

### 4.4 Forward-Looking Workload Clumping (Exam / Project Radar)
* **Trigger Conditions:** $\ge 2$ major assessments (defined as category matching `['Exam', 'Test', 'Project', 'Midterm']` or `points_possible >= 50`) due within a rolling 48-hour window over the next 7 days.
* **Dispatch:** Queued exclusively for the Sunday 6:00 PM Planning Digest.

---

## 5. Notification & Delivery Matrix

> **v1 Channel Strategy:** All v1 notifications are delivered strictly via **Responsive HTML Email** (SendGrid / SMTP). Mobile push channels (Pushover / NTFY) are deferred to future roadmap iterations.

| Alert Type | Priority | Target Audience | Target Channel (v1) | Dispatch Schedule | Payload Contents |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Confirmed Missing Work** | P0 | Parent / Guardian | Email (SendGrid / SMTP) | Weekdays at 5:00 PM | Course, Assignment Name, Due Date, Points Possible, System Source |
| **Grade Drop ($\ge 4\%$)** | P0 | Parent / Guardian | Email (SendGrid / SMTP) | Weekdays at 5:00 PM | Course Name, Previous Grade %, Current Grade %, Delta % |
| **Unexcused Absence / Cut** | P0 | Parent / Guardian | Email (SendGrid / SMTP) | Weekdays at 5:00 PM | Period Number, Course Name, Attendance Code (`A` / `CUT`) |
| **Weekly Planning Digest** | P1 | Parent / Guardian | Email (HTML Digest) | Sunday at 6:00 PM | Full Grade Summary, 7-day Deadlines, Workload Clumping, Weekly Tardy Summary |

---

## 6. State Storage Schema (Google Cloud Firestore)

The engine uses **Google Cloud Firestore** to maintain persistent state snapshots across execution runs. Collection document path: `students/{student_id}`:

```json
{
  "student_id": "student_123",
  "last_synced_at": "2026-08-21T17:00:00Z",
  "session_cookies": {
    "psaid": "encrypted_cookie_string",
    "updated_at": "2026-08-21T17:00:00Z"
  },
  "courses": {
    "ENG101": {
      "name": "English 9",
      "current_percentage": 91.5,
      "letter_grade": "A-",
      "history": [
        {"date": "2026-08-14", "percentage": 95.0},
        {"date": "2026-08-21", "percentage": 91.5}
      ]
    }
  },
  "tracked_assignments": {
    "canvas_98765": {
      "title": "Lord of the Flies Essay Outline",
      "course_id": "ENG101",
      "due_at": "2026-08-19T23:59:00Z",
      "submission_type": "online_upload",
      "canvas_missing": true,
      "first_detected_missing": "2026-08-20T00:05:00Z",
      "alert_dispatched": false
    }
  },
  "attendance_events": [
    {
      "date": "2026-08-21",
      "period": 1,
      "course": "Algebra 1",
      "code": "T",
      "notified": true
    }
  ]
}
```

---

## 7. Implementation Roadmap & Technical Stack

### 7.1 Recommended Stack
* **Runtime:** Python 3.11+ / Playwright Chromium / GCP Cloud Run Job
* **Storage:** Google Cloud Firestore (`students/{student_id}`)
* **Notifications (v1):** Responsive HTML Email via SendGrid / SMTP.
* **Monitoring & Alerting:** GCP Cloud Monitoring (`terraform/monitoring.tf`) log-based alert policy for Cloud Run job execution failures.

### 7.2 Implementation Phases
1. **Phase 0: Infrastructure & Ingestion Proof of Concept**
   * Terraform setup (`terraform/`) for Cloud Run Job, Secret Manager, Firestore, and Guardian CI/CD.
   * Playwright setup for PowerSchool cookie reuse & SAML SSO login.
   * Exit requirement: Cloud Run Job execution logging live student snapshot data from both Canvas and PowerSchool.
2. **Phase 1: MVP Academic Sentinel**
   * Firestore state persistence engine.
   * Asymmetric System Authority Model rules (36h grace period pausing weekends, PowerSchool immediate missing alerts, grade velocity drop checks).
   * SendGrid HTML email notification router (5:00 PM weekday P0 alerts).
3. **Phase 2: Workload Radar & Sunday Digest**
   * Workload clumping evaluator ($\ge 2$ major assessments within 48h window).
   * Sunday 6:00 PM HTML email digest.
nitoring.tf`) log-based alert policy for Cloud Run job failures (eliminates custom app heartbeat overhead)

### 7.2 Implementation Phases
1. **Phase 1: API Harvesters & Authentication**
   * Implement Canvas REST client with Observer Personal Access Token.
   * Implement PowerSchool client handling session login and cookie persistence.
   * Verify rate limits and error-handling backoff strategies.
2. **Phase 2: Entity Matching & State Diffing Engine**
   * Build title-normalization and due-date matching logic across Canvas and PowerSchool.
   * Implement the state store schema to track 14-day snapshots.
   * Build and unit-test the cross-system missing work resolution logic and grace period delays.
3. **Phase 3: Dispatchers & Automation**
   * Implement Pushover / NTFY webhook triggers for P0 alerts.
   * Design and implement the Sunday HTML email template generator.
   * Deploy the service on a daily scheduled cron (5:00 PM weekdays, 6:00 PM Sunday).
