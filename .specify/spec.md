# Feature Specification: Bellmon MVP - Core Academic Sentinel & Noise Reduction

**Feature Name**: Core Academic Sentinel & Noise Reduction  
**Target Phase**: Phase 1 (MVP)  
**Status**: Draft / Ready for Plan  
**Governing Document**: [Project Constitution](../.specify/memory/constitution.md) (v1.0.0)  

---

## 1. Executive Summary & User Value

### 1.1 Problem Statement
Parents monitoring high school students are overwhelmed by portal noise. Standard Canvas LMS notifications fire false missing-assignment alerts for physical paper turned in class, while standard gradebook alerts notify parents too late—long after a grade drop has already occurred.

### 1.2 Solution Overview
Bellmon operates as an unattended background sentinel that ingests data from Canvas LMS and PowerSchool SIS. It cross-evaluates assignment states to eliminate false paper-submission alarms, enforces a 36-hour grace period on digital work to preserve student autonomy, and alerts parents on rolling 7-day grade velocity drops ($\ge 4.0\%$) before end-of-term deficits occur.

---

## 2. User Scenarios & Acceptance Criteria

### Scenario 1: Digital Missing Work Grace Period (Student Autonomy)
* **Given** an assignment in Canvas is overdue (`missing: true`) and turned in via digital upload (`submission_type = online_upload`),
* **And** PowerSchool has no score entered (`-`) and is not marked as missing,
* **When** Bellmon runs its scheduled ingestion sync,
* **Then** Bellmon places the assignment in a 36-hour `GRACE_PERIOD` state and dispatches NO parent alerts.
* **And** if the student submits the assignment within 36 hours, the state resolves silently without notifying parents.
* **And** if 36 hours elapse without submission or score entry, Bellmon dispatches a P0 Push Alert to parents.

### Scenario 2: Paper Submission False-Positive Elimination
* **Given** an assignment in Canvas is flagged as `missing: true`,
* **And** PowerSchool shows a score $> 0$ OR `isCollected: true` (indicating physical hand-in or teacher grading),
* **When** Bellmon evaluates the missing work matrix,
* **Then** Bellmon suppresses the alert completely and logs the status as `SUPPRESSED_PAPER_OR_GRADED`.

### Scenario 3: Confirmed Missing Work Alerting
* **Given** an assignment is explicitly marked as `isMissing: true` or `score: 0` in PowerSchool (or missing in both systems),
* **When** Bellmon runs its daily ingestion sync,
* **Then** Bellmon bypasses the 36-hour grace period buffer and dispatches an immediate P0 Push Alert detailing the course, assignment name, due date, and point loss.

### Scenario 4: Rolling Grade Velocity Drop Warning ($\ge 4.0\%$)
* **Given** a student's course grade average drops by $\ge 4.0\%$ over a rolling 7-day window,
* **When** Bellmon computes course grade snapshots during daily sync,
* **Then** Bellmon identifies the newly entered assignment(s) causing the drop and fires a P0 Push Alert stating:
  - Course Name
  - Previous Grade $\to$ New Grade (e.g., $92.5\% \to 87.0\%$)
  - Impacting Assignment Name and Score

---

## 3. Functional Requirements

### FR-1: Canvas & PowerSchool State Harvesting
- **FR-1.1**: The system MUST harvest missing submissions, due dates, course IDs, assignment names, and submission types (`online_upload`, `on_paper`, `none`) from Canvas REST endpoints.
- **FR-1.2**: The system MUST harvest overall course percentages, letter grades, assignment scores, and status flags (`isMissing`, `isCollected`, `isLate`) from PowerSchool.

### FR-2: Cross-System Missing Work Resolution Engine
- **FR-2.1**: The system MUST cross-reference Canvas assignment IDs and names against PowerSchool gradebook items.
- **FR-2.2**: The system MUST enforce the following matrix:
  - Canvas missing + PowerSchool score $>0$ or `Collected: true` $\to$ **Suppress alert**.
  - Canvas missing + PowerSchool blank (`-`) + digital upload $\to$ **Apply 36-hour Grace Period**.
  - Canvas missing + PowerSchool `isMissing: true` or `score: 0` $\to$ **Immediate P0 Push Alert**.
  - Canvas missing post-36h grace period $\to$ **Post-Grace P0 Push Alert**.

### FR-3: Grade Velocity Drop Evaluator
- **FR-3.1**: The system MUST maintain daily course grade snapshots for at least 14 rolling days.
- **FR-3.2**: The system MUST compute $\Delta = \text{Grade}_{t-7} - \text{Grade}_{current}$ for every course on each sync run.
- **FR-3.3**: When $\Delta \ge 4.0\%$, the system MUST isolate the assignment entered within that 7-day interval that caused the largest point deduction.

### FR-4: Email Notification Router & Deduplication Ledger
- **FR-4.1**: The system MUST format and dispatch structured email notifications (HTML & plain text) to registered family email addresses.
- **FR-4.2**: The system MUST maintain an idempotent alert ledger in Google Cloud Firestore to ensure zero duplicate notifications are sent for the same missing assignment or grade drop event.

---

## 4. Non-Functional & Governance Requirements

- **NFR-1 (Zero-Touch Operational Model)**: System MUST run unattended via scheduled background jobs without requiring manual web dashboard access.
- **NFR-2 (Constitution Compliance - Principle 1)**: Digital missing assignments MUST NOT notify parents prior to 36 hours of first detection.
- **NFR-3 (Constitution Compliance - Principle 2)**: 100% of paper turned-in work or teacher-graded items MUST be suppressed.
- **NFR-4 (Constitution Compliance - Principle 3)**: Grade drop alerts MUST specify the exact impacting assignment title.

---

## 5. Success Criteria

- **SC-1 (Zero False Alarms)**: 100% of physical paper turned in or teacher-graded assignments generate zero parent alerts.
- **SC-2 (Student Autonomy Protection)**: 100% of digital missing assignments observe a minimum 36-hour buffer before parent push.
- **SC-3 (Timely Velocity Warnings)**: 100% of course drops $\ge 4.0\%$ trigger an alert specifying the impacting item within 24 hours of grade entry.
- **SC-4 (Idempotency)**: 0 duplicate push notifications are dispatched for any single event.

---

## 6. Bounded Scope & Out of Scope (Phase 1 MVP)

- **Out of Scope for MVP**:
  - Attendance tracking (deferred to Phase 3)
  - Sunday Night HTML Email Digest (deferred to Phase 2)
  - Web UI configuration portal (all configuration managed via local config file)
  - Multi-student UI dashboards
