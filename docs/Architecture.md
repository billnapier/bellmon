# Technical Architecture & System Design - Bellmon (Bellarmine Monitor)

This document formalizes the technical architecture, technology stack, and component interactions for **Bellmon (Bellarmine Monitor)**, derived from requirements in `Bellmon_PRD.md` and ratified decisions.

---

## 1. System Overview Architecture

```
                  ┌─────────────────────────────────────┐
                  │       GCP Cloud Scheduler           │
                  │ - 5:00 PM Weekdays (P0 Daily Run)   │
                  │ - 6:00 PM Sundays  (P1 Digest Run)  │
                  └──────────────────┬──────────────────┘
                                     │ Trigger
                                     ▼
                  ┌─────────────────────────────────────┐
                  │       GCP Cloud Run Job             │
                  │ (Docker: Playwright Python Runtime) │
                  └──────┬───────────────────────┬──────┘
                         │                       │
     ┌───────────────────┴───────┐       ┌───────┴───────────────────┐
     ▼                           ▼       ▼                           ▼
┌─────────┐             ┌─────────────────┐                     ┌─────────┐
│ Canvas  │             │   PowerSchool   │                     │ SendGrid│
│ REST API│             │ Headless (SAML) │                     │ Email   │
└────┬────┘             └────────┬────────┘                     └────▲────┘
     │                           │                                   │
     └─────────────┬─────────────┘                                   │
                   ▼                                                 │
      ┌─────────────────────────┐                                    │
      │ Business Logic Engine   │                                    │
      │ - Grace Period (36h)    │                                    │
      │ - Delta Drop (>= 4.0%)  │                                    │
      │ - Attendance Anomalies  │────────────────────────────────────┘
      │ - Workload Clumping     │          Dispatch HTML Email
      └────────────┬────────────┘
                   ▼
      ┌─────────────────────────┐
      │ Google Cloud Firestore  │
      │ - Grade Snapshots (14d) │
      │ - Assignment Ledger     │
      │ - Dispatch Idempotency  │
      └─────────────────────────┘
```

---

## 2. Technology Stack & Infrastructure

| Layer / Subsystem | Technology Choice | Details & Rationale |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.11+ | High ecosystem support for web automation, HTML parsing, and cloud SDKs. |
| **Canvas Ingestion** | Canvas REST API | Connects via Personal Access Token (`/api/v1/users/:observee_id/missing_submissions`, `/api/v1/courses/:course_id/assignments`). |
| **PowerSchool Ingestion** | Playwright (Python) | Headless browser automation handling SAML SSO login (`powerschool.bcp.org`), session persistence, and gradebook/attendance scraping. |
| **Execution Platform** | GCP Cloud Run Jobs | Containerized execution environment running on demand; 100% serverless and zero-cost within GCP free tier. |
| **Job Scheduling** | GCP Cloud Scheduler | Cron-based HTTP triggers calling Cloud Run jobs daily (5:00 PM weekdays for P0 alerts; 6:00 PM Sunday for P1 digests). |
| **State Storage** | Google Cloud Firestore | Serverless document database storing student state snapshots, assignment ledgers, and notification history. |
| **Notification Engine** | SendGrid Web API | Delivers responsive HTML emails for both P0 urgent alerts and P1 Sunday planning digests. |
| **Secrets Management** | GCP Secret Manager | Securely stores Canvas API tokens, SendGrid API keys, and PowerSchool SSO credentials. |

---

## 3. Data Ingestion & Ingestion Strategy

### 3.1 Canvas LMS Ingestion
* **Endpoint:** `GET /api/v1/users/:observee_id/missing_submissions` & `GET /api/v1/courses/:course_id/assignments`.
* **Captured Attributes:** `assignment_id`, `name`, `due_at`, `submission_types`, `points_possible`, `has_submitted_submissions`.

### 3.2 PowerSchool SIS SAML SSO Ingestion
* **Mechanism:** Playwright Chromium headless browser session.
* **Workflow:**
  1. Playwright navigates to `https://powerschool.bcp.org/guardian/home.html`.
  2. Follows SAML SSO redirect flow, submitting stored SSO credentials.
  3. Captures session cookies (`JSESSIONID`, `psaid`) and parses course list, letter grades, percentage, and period attendance.
  4. Fetches per-course assignment details at `/guardian/scores.html?frn=...`.

---

## 4. State Storage Schema (Firestore)

Firestore maintains a single primary document per monitored student: `students/{student_id}`:

```json
{
  "student_id": "bcp_student_123",
  "last_synced_at": "2026-08-21T17:00:00Z",
  "courses": {
    "ALG2_H": {
      "name": "Algebra 2 Honors",
      "current_percentage": 92.4,
      "letter_grade": "A-",
      "history": [
        {"date": "2026-08-14", "percentage": 96.5},
        {"date": "2026-08-21", "percentage": 92.4}
      ]
    }
  },
  "tracked_assignments": {
    "canvas_109283": {
      "title": "Polynomial Functions Quiz",
      "course_id": "ALG2_H",
      "due_at": "2026-08-19T23:59:00Z",
      "status": "GRACE_PERIOD",
      "first_detected_missing": "2026-08-20T00:05:00Z",
      "alert_dispatched": false
    }
  },
  "attendance_events": [
    {
      "date": "2026-08-21",
      "period": 1,
      "course": "Algebra 2 Honors",
      "code": "T",
      "notified": true
    }
  ]
}
```

---

## 5. Alert Heuristics & Business Rules

1. **Digital Missing Work Grace Period:** Digital Canvas assignments (`online_upload`) trigger a 36-hour delay window (`GRACE_PERIOD`) before dispatching a parent email, allowing student self-correction.
2. **Confirmed Missing Work:** Bypasses grace period if PowerSchool confirms `isMissing: true` or `score: 0`.
3. **Paper Work Suppression:** If Canvas reports missing but PowerSchool shows `score > 0` or `isCollected: true`, alert is suppressed (`SUPPRESSED`).
4. **Grade Velocity Drop:** Triggers P0 alert if rolling 7-day course grade drops by $\Delta \ge 4.0\%$, highlighting the specific assignment causing max point loss.
5. **Attendance Anomaly:** Triggers P0 alert for period codes $\in \{\text{'A'}, \text{'T'}, \text{'U'}, \text{'CUT'}\}$.
6. **Workload Clumping:** Flags Sunday digest banner if $\ge 2$ major assessments (tests, exams, projects or $\ge 50$ pts) fall within any 48-hour window over the next 7 days.
