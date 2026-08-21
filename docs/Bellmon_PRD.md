# Product Definition: Student Academic & Workload Sentinel

## 1. Executive Summary & Goals

### 1.1 Overview
The **Student Academic & Workload Sentinel** is an automated, event-driven monitoring pipeline engineered to ingest academic, assignment, and attendance data from **Canvas LMS** and **PowerSchool SIS**. 

The system provides early-warning visibility into student risk factors—specifically unsubmitted assignments, steep grade trajectory drops, attendance anomalies, and high-stakes workload clumping—while strictly preserving student autonomy through heuristic-based noise filtering, configurable grace periods, and zero required app check-ins.

### 1.2 Core Objectives
* **Zero-Touch Monitoring:** Deliver all actionable insights via direct push notifications (Pushover / NTFY) or structured email digests; eliminate manual portal logins and app-checking.
* **Noise & False-Positive Elimination:** Cross-reference Canvas submission states against PowerSchool grading records to resolve paper submission mismatches and in-progress grading artifacts.
* **Proactive Trajectory Tracking:** Alert on velocity drops ($\Delta \ge 4.0\%$) and upcoming workload clustering rather than waiting for formal report cards or end-of-term deficits.
* **Student Autonomy & Grace Periods:** Provide configurable delay windows (e.g., 24–36 hours) before alerting parents on digital missing assignments, empowering students to self-advocate and resolve discrepancies with teachers directly.

---

## 2. System Architecture

```
 ┌──────────────────────┐        ┌──────────────────────┐
 │      Canvas LMS      │        │    PowerSchool SIS   │
 │   - REST API         │        │   - Mobile REST API  │
 │   - iCal Due Dates   │        │   - Attendance       │
 └──────────┬───────────┘        └──────────┬───────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │   Scheduled Ingestion Engine  │
            │   (Daily Cron / Serverless)   │
            │   - Fetch latest state        │
            │   - Correlate entities        │
            │   - Compute state diffs       │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       State Store (DB)        │
            │   - Assignment status cache   │
            │   - Grade trajectory history  │
            │   - Alert dispatch ledger     │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Alert Rules Engine       │
            │   - Grace period verification │
            │   - Delta threshold checks    │
            │   - Workload clumping analysis│
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Notification Router      │
            ├───────────────┬───────────────┤
            │ P0: Push Alert│ P1: Digest    │
            │ (NTFY/Pushover│ (Weekly Email)│
            └───────────────┴───────────────┘
```

---

## 3. Data Ingestion & Integration Layer

### 3.1 Canvas LMS Ingestion
Canvas serves as the primary system for digital assignments, project descriptions, upcoming due dates, and learning materials.

* **API Endpoints:**
  * `GET /api/v1/users/:observee_id/missing_submissions`: Retrieves overdue assignments lacking a submission record.
  * `GET /api/v1/courses/:course_id/assignments`: Fetches complete course assignment structures, category weightings, and rubric details.
  * `GET /api/v1/calendar_events` (or iCal `.ics` feed subscription): Ingests forward-looking calendar entries for exam and deadline radar tracking.
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

* **API Endpoints:**
  * PowerSchool Parent/Guardian REST Mobile Gateway (`/guardian/dashboard` or `/api/v1/student/:id/grades`).
* **Extracted Attributes:**
  * `course_name` (String)
  * `current_percentage` (Float)
  * `letter_grade` (String: e.g., 'A-', 'B+')
  * `teacher_name` (String)
  * `teacher_comments` (String)
  * `period_attendance` (Array of objects: `{ date, period, code, description }`)
  * `assignment_records` (Array of objects with status flags: `isMissing`, `isLate`, `isCollected`, `isExempt`, `score`, `pointsPossible`)

---

## 4. Heuristic & Business Logic Engine

### 4.1 Cross-System Missing Work Resolution Matrix
To prevent false alarms arising from physical paper submissions or delayed teacher data entry, the rules engine cross-evaluates Canvas and PowerSchool states before dispatching alerts.

```
IF Canvas.missing == True:
    IF Canvas.submission_types CONTAINS "on_paper" OR "none":
        DEFER to PowerSchool.isMissing
    ELSE IF PowerSchool.isCollected == True OR PowerSchool.score > 0:
        SUPPRESS (Turned in on paper / manually recorded)
    ELSE IF PowerSchool.isMissing == True OR PowerSchool.score == 0:
        EMIT Alert(P0, "Confirmed Missing Assignment")
    ELSE:
        APPLY GracePeriod(36 Hours)
        IF Still Unsubmitted after GracePeriod:
            EMIT Alert(P0, "Missing Digital Assignment (Post-Grace)")
```

#### Detailed Case Resolution Table

| Canvas Status | PowerSchool Status | Reality / Root Cause | Engine Action |
| :--- | :--- | :--- | :--- |
| `missing: true` | Score $> 0$ or `Collected: true` | Physical worksheet handed in; teacher graded or checked in | **Suppress alert** (False positive eliminated). |
| `missing: true` | Blank score (`-`), no missing flag | Turned in on paper or in-progress teacher grading | **Apply 36h Grace Period** before evaluating again. |
| `missing: true` | `score: 0` or `isMissing: true` | Teacher explicitly confirmed work was not received | **Fire P0 Push Alert** immediately. |
| `missing: false` | `isMissing: true` or `score: 0` | In-class task / paper exam not tracked in Canvas | **Fire P0 Push Alert** immediately. |

### 4.2 Grade Trajectory & Velocity Drop Detection
* **Mathematical Trigger:**
  $$\Delta = \text{Grade}_{t-\text{prev}} - \text{Grade}_{t-\text{curr}} \ge 4.0\%$$
  Evaluated over a rolling 7-day window per course.
* **Payload Isolation:** The engine correlates the delta with the specific assignment ID or zero entered within that interval and includes the assignment title and point loss in the alert body.

### 4.3 Attendance Anomaly Processing
* **Trigger Conditions:** Period attendance code $\in \{\text{'A' (Unexcused Absence)}, \text{'T' (Tardy)}, \text{'U' (Unverified)}, \text{'CUT'}\}$.
* **Suppression Conditions:** Standard present or authorized excused codes ($\{\text{'P' (Present)}, \text{'E' (Excused)}, \text{'EX'}, \text{'ACT' (School Activity)}\}$) are ignored.
* **Dispatch:** Immediate P0 push alert including the class period, course title, and timestamp.

### 4.4 Forward-Looking Workload Clumping (Exam / Project Radar)
* **Trigger Conditions:** $\ge 2$ major assessments (defined as category matching `['Exam', 'Test', 'Project', 'Midterm']` or `points_possible >= 50`) due within a rolling 48-hour window over the next 7 days.
* **Dispatch:** Queued exclusively for the Sunday Planning Digest to assist with weekly backwards planning without creating daily alert fatigue.

---

## 5. Notification & Delivery Matrix

| Alert Type | Priority | Target Channel | Dispatch Schedule | Payload Contents |
| :--- | :--- | :--- | :--- | :--- |
| **Confirmed Missing Work** | P0 | Push (Pushover / NTFY) | Daily at 5:00 PM | Course, Assignment Name, Due Date, Points Possible, System Source |
| **Grade Drop ($\ge 4\%$)** | P0 | Push (Pushover / NTFY) | Daily at 5:00 PM | Course, Old Grade $\to$ New Grade, Impacting Assignment Name & Score |
| **Attendance Anomaly** | P0 | Push (Pushover / NTFY) | Real-time / Daily at 4:00 PM | Period Number, Course Name, Teacher, Attendance Code |
| **Weekly Planning Digest** | P1 | Email (HTML) | Sunday at 6:00 PM | Full Course Grade Summary, Upcoming 7-day Deadlines, Workload Clumping Warnings |

---

## 6. State Storage Schema

The engine maintains a lightweight state cache (e.g., Firestore document or local SQLite database) to compute running diffs across sync runs.

```json
{
  "student_id": "student_123",
  "last_synced_at": "2026-08-20T17:00:00Z",
  "courses": {
    "ENG101": {
      "name": "English 9",
      "current_percentage": 91.5,
      "letter_grade": "A-",
      "history": [
        {"date": "2026-08-13", "percentage": 95.0},
        {"date": "2026-08-20", "percentage": 91.5}
      ]
    },
    "MATH201": {
      "name": "Algebra 1",
      "current_percentage": 88.0,
      "letter_grade": "B+",
      "history": [
        {"date": "2026-08-13", "percentage": 88.0},
        {"date": "2026-08-20", "percentage": 88.0}
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
      "powerschool_status": "unrecorded",
      "first_detected_missing": "2026-08-20T00:05:00Z",
      "alert_dispatched": false
    }
  },
  "attendance_events": [
    {
      "date": "2026-08-20",
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
* **Runtime:** Python 3.11+ / Serverless (Google Cloud Run / AWS Lambda / Local Cron)
* **Storage:** Google Cloud Firestore, SQLite, or local JSON state store
* **Push Notifications:** Pushover API or self-hosted NTFY instance
* **Email Delivery:** SendGrid, AWS SES, or SMTP for the Sunday HTML digest

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
