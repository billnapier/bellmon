# Bellmon (Bellarmine Monitor)

**Bellmon (Bellarmine Monitor)** is an automated, event-driven academic and workload monitoring sentinel engineered to ingest student performance data from **Canvas LMS** and **PowerSchool SIS**.

Built specifically for Bellarmine parents and students, Bellmon delivers proactive, zero-touch early warnings into missing assignments, grade trajectory drops, attendance anomalies, and upcoming workload clusters—while preserving student autonomy through heuristic noise filtering and a 36-hour grace period buffer.

---

## Key Features & Value Proposition

* **Zero-Touch Monitoring:** Responsive HTML email alerts and weekly digests (SendGrid / SMTP) replace manual portal logins.
* **Noise & False-Alarm Suppression:** Uses an Asymmetric System Authority Model to eliminate false alerts for paper/in-class assignments.
* **36-Hour Student Autonomy Grace Period:** Gives students a 36-hour buffer (pausing on weekends) on overdue digital assignments to self-advocate and turn in work before emailing parents.
* **Proactive Grade Velocity Drop Warnings:** Alerts immediately on rolling course grade drops ($\ge 4.0\%$) compared to historical snapshots ($[t-10, t-7]$ days).
* **Workload Radar:** Identifies heavy 48-hour exam/project clusters in advance for Sunday night weekly planning digests.

---

## Documentation Links

* [Product Requirements Document (PRD)](docs/Prd.md) - Full system specification and heuristic business logic matrix.
* [Technical Architecture](docs/Architecture.md) - System architecture, Playwright scraping design, and GCP Cloud Run Job setup.
* [Critical User Journeys (CUJs)](docs/CUJ.md) - Detailed user personas, triggers, workflows, and outputs across 7 core use cases.
* [Product Feature Roadmap](docs/Roadmap.md) - Phased deliverable roadmap (Phase 0 Proof of Concept, MVP Sentinel, Workload Radar).

---

## Project Structure

```
bellmon/
├── docs/
│   ├── Prd.md                 # Product Requirements Document
│   ├── Architecture.md        # Technical Architecture & Design
│   ├── CUJ.md                 # Critical User Journeys
│   ├── Roadmap.md             # Phased Product Roadmap
│   ├── code-of-conduct.md
│   └── contributing.md
└── README.md
```
