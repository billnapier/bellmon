# Implementation Plan: Bellmon MVP - Core Academic Sentinel & Noise Reduction

**Feature**: Core Academic Sentinel & Noise Reduction  
**Specification**: [.specify/spec.md](../.specify/spec.md)  
**Governing Document**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)  

---

## 1. Technical Architecture & Infrastructure

### 1.1 Deployment & Execution Topology
* **Target Environment**: **Google Cloud Run Job** (Serverless container runtime).
* **Trigger Mechanism**: **Google Cloud Scheduler** (Cron trigger executing daily at 5:00 PM).
* **Container Packaging**: Lightweight Docker container (`Dockerfile` based on `python:3.11-slim`).

```
 ┌──────────────────────┐        ┌──────────────────────┐
 │      Canvas LMS      │        │    PowerSchool SIS   │
 │   - REST API         │        │   - Mobile REST API  │
 └──────────┬───────────┘        └──────────┬───────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       Google Cloud Run        │
            │   (Daily Serverless Job)      │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │    Google Cloud Firestore     │
            │  - Grade Snapshots (14 days)  │
            │  - Assignment Grace State     │
            │  - Alert Deduplication Ledger │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Alert Rules Engine       │
            │  - Missing Work Matrix        │
            │  - 36h Grace Evaluator        │
            │  - Grade Drop Delta Evaluator │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Notification Router      │
            │    - Email Delivery (SMTP)    │
            └───────────────────────────────┘
```

---

## 2. Constitution Alignment Check

| Principle | Requirement | Verification Method in Design | Status |
| :--- | :--- | :--- | :--- |
| **P1: Student Autonomy** | 36-hour delay buffer before alerting on digital missing items | Verified in `missing_work.py` by comparing `current_time - first_detected_missing >= 36h`. | ✅ PASS |
| **P2: Cross-System Noise Elimination** | Suppress alerts if PowerSchool score $>0$ or `isCollected: true` | Verified in `missing_work.py` by evaluating PS score & collection flags prior to queuing alerts. | ✅ PASS |
| **P3: Proactive Grade Velocity Drop** | Alert on 7-day rolling drop $\ge 4.0\%$ with impacting item | Verified in `trajectory.py` by comparing 7-day snapshot delta and isolating highest point loss. | ✅ PASS |
| **P4: Zero-Touch Delivery** | Unattended delivery via Email notifications | Verified via scheduled Cloud Run Job + Cloud Scheduler and `email.py` router. | ✅ PASS |
| **P5: Workload Radar** | Highlight 48h exam/project clusters in weekly digest | Deferred to Phase 2 per roadmap. | ⏩ DEFERRED |

---

## 3. Data Schema & Firestore Storage (`bellmon/storage/firestore.py`)

Bellmon utilizes **Google Cloud Firestore** as a serverless state store.

### 3.1 Collections Schema

#### Collection: `grade_snapshots`
- Document ID: `{course_id}_{YYYY-MM-DD}`
- Fields:
  - `course_id` (string)
  - `course_name` (string)
  - `percentage` (float)
  - `letter_grade` (string)
  - `snapshot_date` (timestamp)

#### Collection: `assignment_states`
- Document ID: `{canvas_assignment_id}`
- Fields:
  - `course_id` (string)
  - `title` (string)
  - `submission_type` (string)
  - `due_at` (timestamp)
  - `first_detected_missing` (timestamp)
  - `status` (string: `GRACE_PERIOD` | `RESOLVED` | `SUPPRESSED` | `ALERT_DISPATCHED`)
  - `last_updated` (timestamp)

#### Collection: `alert_ledger`
- Document ID: `{event_id}`
- Fields:
  - `event_type` (string: `MISSING_WORK_POST_GRACE` | `CONFIRMED_MISSING` | `GRADE_DROP`)
  - `dispatched_at` (timestamp)
  - `recipient_email` (string)
  - `payload_json` (map)

---

## 4. Module Specifications

### 4.1 Configuration Loader (`bellmon/config.py`)
- Reads environment variables / GCP secrets via Pydantic Settings:
  - `CANVAS_BASE_URL`, `CANVAS_API_TOKEN`
  - `POWERSCHOOL_BASE_URL`, `POWERSCHOOL_USERNAME`, `POWERSCHOOL_PASSWORD`
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFICATION_EMAIL_TO`, `NOTIFICATION_EMAIL_FROM`
  - `GCP_PROJECT_ID`
  - `GRACE_PERIOD_HOURS` (Default: 36)
  - `GRADE_DROP_THRESHOLD` (Default: 4.0)

### 4.2 Harvesters (`bellmon/harvesters/`)
- **Canvas Harvester (`canvas.py`)**: REST harvester for missing submissions and assignment details.
- **PowerSchool Harvester (`powerschool.py`)**: Harvester for course percentages and assignment marks.

### 4.3 Rules Engine (`bellmon/engine/`)
- **Missing Work Matrix (`missing_work.py`)**: Evaluates 36h grace period and paper suppression logic.
- **Grade Velocity Drop Evaluator (`trajectory.py`)**: Evaluates 7-day Firestore snapshots and flags drops $\ge 4.0\%$.

### 4.4 Email Notification Router (`bellmon/notifications/email.py`)
- Formats clean, structured email alerts (Text & HTML).
- Sends emails via SMTP or cloud email gateway.
- Writes `event_id` to Firestore `alert_ledger` collection for deduplication.

### 4.5 Packaging & Containerization
- `Dockerfile`: Multi-stage build for Python 3.11 runtime.
- `deploy.sh` / Terraform script for Cloud Run Job deployment and Cloud Scheduler creation.

---

## 5. Implementation Task Hierarchy

1. **Task 1: Core Scaffolding & Configuration** (`config.py`, `config.example.toml`, `requirements.txt`)
2. **Task 2: Firestore State Store** (`storage/firestore.py`)
3. **Task 3: Harvester Clients** (`harvesters/canvas.py`, `harvesters/powerschool.py`)
4. **Task 4: Rules Engine & Heuristics** (`engine/missing_work.py`, `engine/trajectory.py`)
5. **Task 5: Email Router & Deduplication** (`notifications/email.py`)
6. **Task 6: Containerization & Cloud Run Manifests** (`Dockerfile`, `cli.py`)
7. **Task 7: Test Suite & Verification** (`tests/`)
