# Product Feature Roadmap - Bellmon (Bellarmine Monitor)

This roadmap outlines the phased deliverable plan for Bellmon features, organized by product maturity and user value.

## Phase 0: Infrastructure Setup & End-to-End Proof of Concept

Focus: Establish foundational cloud infrastructure, automated CI/CD pipeline, containerized Playwright runtime, sub-daily Cloud Run execution, and dual-system data harvesting.

### Key Output
* **Cloud Run Batch Execution Verification:** A containerized GCP Cloud Run batch job scheduled for sub-daily execution (e.g., every 6 or 12 hours) that fetches live observer data from both **Canvas** (courses/assignments) and **PowerSchool** (grades/attendance snapshots), printing student snapshot records to stdout/logs.
* **Foundational Infrastructure:**
  * Declarative Terraform IaC setup (`terraform/`) for Cloud Run Job, Cloud Scheduler trigger, Secret Manager, Firestore, and IAM permissions.
  * `abcxyz/guardian` GitHub Actions workflow for automated Terraform actuation (`guardian plan` on PR, `guardian apply` on merge to `main`).
  * Playwright headless browser setup for PowerSchool cookie reuse & SAML SSO authentication.
  * Direct Production ("Test in Prod") deployment pipeline.

*(Note: Phase 0 does not implement end-user notification rules, but serves as a strict mandatory gate validating core connectivity, SAML authentication, and batch execution before proceeding to feature development).*

---

## Phase 1: MVP - Core Academic & Attendance Sentinel

Focus: Eliminate false missing-assignment alarms, preserve student autonomy, catch rapid grade drops early, and alert on unexcused attendance anomalies.

### Features
* **Asymmetric System Authority Missing Work Resolution**
  * Correlate Canvas digital missing status against PowerSchool grade records independently.
  * Automatically suppress false alerts when work is handed in on paper or graded in class.
* **36-Hour Student Autonomy Grace Period**
  * Apply a 36-calendar-hour delay buffer (pausing on weekends) to digital missing assignments before emailing parents.
  * Sub-daily Cloud Run execution ensures 36-hour grace expiration is evaluated accurately near its target timestamp.
* **Confirmed Missing Work Direct Alerting**
  * Instantly alert on assignments explicitly marked as zero or missing in PowerSchool, bypassing the grace period buffer.
* **Grade Velocity Drop Warnings ($\ge 4.0\%$)**
  * Track rolling course grade trajectories in Cloud Firestore.
  * Fire urgent email alerts when a course grade drops by $\ge 4.0\%$ compared to historical snapshot ($[t-10, t-7]$ days).
  * *Silent Warming Protocol:* During initial deployment (Days 1–7), history silently accumulates until baseline snapshots exist.
* **Attendance Anomaly Sentinel (P0 Alerting)**
  * Evaluate period-level attendance data harvested from PowerSchool.
  * Dispatch urgent weekday email alerts for unexcused absences (`A`) or class cuts (`CUT`).
* **Direct Email Alerts (Resend / SMTP)**
  * Deliver urgent P0 notification payloads directly to parent/guardian email addresses.

---

## Phase 2: Workload Radar & Sunday Digest

Focus: Help families plan ahead for heavy academic weeks and eliminate Sunday-night surprises.

### Features
* **Workload Clumping Radar**
  * Scan upcoming 7-day assignment and exam schedules.
  * Identify and highlight high-stakes workload clusters ($\ge 2$ major exams, projects, or papers due within a 48-hour window).
* **Sunday Evening Weekly Planning Digest**
  * Deliver a comprehensive HTML email digest every Sunday at 6:00 PM.
  * Include current grade standings across all courses, upcoming 7-day deadline timeline, workload clumping warning banners, and weekly tardy (`T`) / unverified (`U`) attendance summary.

---

## Phase 3: Customization & Multi-Student Oversight

Focus: Provide granular family configuration and expand scope to multiple observees.

### Features
* **Customizable Thresholds & Grace Periods**
  * Allow families to configure custom grade drop trigger percentages (e.g., $3\%$ vs $5\%$) and custom grace period durations (e.g., 24h vs 48h).
* **Multi-Student Oversight**
  * Support monitoring multiple siblings or observees in a single unified notification feed.

