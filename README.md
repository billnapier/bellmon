# Bellmon (Bellarmine Monitor)

**Bellmon (Bellarmine Monitor)** is an automated, event-driven academic and workload monitoring sentinel engineered to ingest student performance data from **Canvas LMS** and **PowerSchool SIS**.

Built specifically for Bellarmine parents and students, Bellmon delivers proactive, zero-touch early warnings into missing assignments, grade trajectory drops, attendance anomalies, and upcoming workload clusters—while preserving student autonomy through heuristic noise filtering and a 36-hour grace period buffer.

---

## Key Features & Value Proposition

* **Zero-Touch Monitoring:** Push notifications (Pushover / NTFY) and weekly digests replace manual portal logins.
* **Noise & False-Alarm Suppression:** Cross-references Canvas submission flags against PowerSchool gradebook records to automatically suppress false alerts for paper/in-class assignments.
* **36-Hour Student Autonomy Grace Period:** Gives students a 36-hour buffer on overdue digital assignments to self-advocate and turn in work before notifying parents.
* **Proactive Grade Velocity Drop Warnings:** Alerts immediately on rolling 7-day course grade drops ($\ge 4.0\%$) and pinpoints the exact assignment responsible.
* **Workload Radar:** Identifies heavy 48-hour exam/project clusters in advance for Sunday night weekly planning.

---

## Documentation Links

* [Product Requirements Document (PRD)](docs/Bellmon_PRD.md) - Full system specification and heuristic business logic matrix.
* [Critical User Journeys (CUJs)](docs/CUJ.md) - Detailed user personas, triggers, workflows, and outputs across 7 core use cases.
* [Product Feature Roadmap](docs/Roadmap.md) - Phased deliverable roadmap (MVP, Workload Radar, Attendance Sentinel).

---

## Project Structure

```
bellmon/
├── Bellmon_PRD.md             # Master PRD root reference
├── docs/
│   ├── Bellmon_PRD.md         # Product Requirements Document
│   ├── CUJ.md                 # Critical User Journeys
│   ├── Roadmap.md             # Phased Product Roadmap
│   ├── code-of-conduct.md
│   └── contributing.md
└── README.md
```
