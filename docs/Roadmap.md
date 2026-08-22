# Product Feature Roadmap - Bellmon (Bellarmine Monitor)

This roadmap outlines the phased deliverable plan for Bellmon features, organized by product maturity and user value.

## Phase 0: Infrastructure Setup & End-to-End Proof of Concept

Focus: Establish foundational cloud infrastructure, automated CI/CD pipeline, containerized Playwright runtime, and dual-system data harvesting.

### Key Output
* **Cloud Run Batch Execution Verification:** A containerized GCP Cloud Run batch job that executes on demand, fetches live observer data from both **Canvas** (courses/assignments) and **PowerSchool** (grades/attendance snapshots), and prints student snapshot records to stdout/logs.
* **Foundational Infrastructure:**
  * Declarative Terraform IaC setup (`terraform/`) for Cloud Run Job, Secret Manager, Firestore, and IAM permissions.
  * `abcxyz/guardian` GitHub Actions workflow for automated Terraform actuation (`guardian plan` on PR, `guardian apply` on merge to `main`).
  * Playwright headless browser setup for PowerSchool cookie reuse & SAML SSO authentication.
  * Direct Production ("Test in Prod") deployment pipeline.

*(Note: Phase 0 does not implement end-user CUJs or alert heuristics, but validates core connectivity, authentication, and batch execution layer upon which all sentinel logic is built).*

---

## Phase 1: MVP - Noise Reduction & Core Academic Sentinel

Focus: Eliminate false missing-assignment alarms, preserve student autonomy, and catch rapid grade drops early.

### Features
* **Asymmetric System Authority Missing Work Resolution**
  * Correlate Canvas digital missing status against PowerSchool grade records independently.
  * Automatically suppress false alerts when work is handed in on paper or graded in class.
* **36-Hour Student Autonomy Grace Period**
  * Apply a 36-calendar-hour delay buffer (pausing on weekends) to digital missing assignments before emailing parents.
  * Give students time to self-advocate and turn in work or resolve issues directly with teachers.
* **Confirmed Missing Work Direct Alerting**
  * Instantly alert on assignments explicitly marked as zero or missing in PowerSchool, bypassing the grace period buffer.
* **Grade Velocity Drop Warnings ($\ge 4.0\%$)**
  * Track rolling course grade trajectories in Cloud Firestore.
  * Fire urgent email alerts when a course grade drops by $\ge 4.0\%$ compared to historical snapshot ($[t-10, t-7]$ days).
* **Direct Email Alerts (5:00 PM Weekday Batch)**
  * Deliver urgent P0 notification payloads directly to parent/guardian email addresses via SendGrid / SMTP.

---

## Phase 2: Workload Radar & Weekly Planning

Focus: Help families plan ahead for heavy academic weeks and eliminate Sunday-night surprises.

### Features
* **Workload Clumping Radar**
  * Scan upcoming 7-day assignment and exam schedules.
  * Identify and highlight high-stakes workload clusters ($\ge 2$ major exams, projects, or papers due within a 48-hour window).
* **Sunday Evening Weekly Planning Digest**
  * Deliver a comprehensive HTML email digest every Sunday at 6:00 PM.
  * Include current grade standings across all courses, upcoming 7-day deadline timeline, and prominent workload clumping warning banners.

---

## Phase 3: Attendance Sentinel & Customization

Focus: Expand oversight into daily attendance anomalies and provide granular family configuration.

### Features
* **Attendance Anomaly Alerts**
  * Monitor period-level attendance records daily in the 5:00 PM batch run.
  * Dispatch alerts for unexcused absences (`A`) or class cuts (`CUT`).
* **Customizable Thresholds & Grace Periods**
  * Allow families to configure custom grade drop trigger percentages (e.g., $3\%$ vs $5\%$) and custom grace period durations (e.g., 24h vs 48h).
* **Multi-Student Oversight**
  * Support monitoring multiple siblings or observees in a single unified notification feed.
