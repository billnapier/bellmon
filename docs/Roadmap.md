# Product Feature Roadmap - Bellmon (Bellarmine Monitor)

This roadmap outlines the phased deliverable plan for Bellmon features, organized by product maturity and user value.

---

## Phase 1: MVP - Noise Reduction & Core Academic Sentinel

Focus: Eliminate false missing-assignment alarms, preserve student autonomy, and catch rapid grade drops early.

### Features
* **Cross-System Missing Work Resolution**
  * Correlate Canvas digital missing status against PowerSchool grade records.
  * Automatically suppress false alerts when work is handed in on paper or graded in class.
* **36-Hour Student Autonomy Grace Period**
  * Apply a 36-hour delay buffer to digital missing assignments before notifying parents.
  * Give students time to self-advocate and turn in work or resolve issues directly with teachers.
* **Confirmed Missing Work Direct Alerting**
  * Instantly alert on assignments explicitly marked as zero or missing in PowerSchool, bypassing the grace period buffer.
* **Grade Velocity Drop Warnings ($\ge 4.0\%$)**
  * Track rolling 7-day course grade trajectories.
  * Fire urgent alerts when a grade drops by $\ge 4.0\%$, calling out the specific assignment responsible for the drop.
* **Direct Mobile Push Alerts**
  * Deliver urgent P0 notification payloads directly to parent/student devices via push notification channels (Pushover / NTFY).

---

## Phase 2: Workload Radar & Weekly Planning

Focus: Help families plan ahead for heavy academic weeks and eliminate Sunday-night surprises.

### Features
* **Workload Clumping Radar**
  * Scan upcoming 7-day assignment and exam schedules.
  * Identify and highlight high-stakes workload clusters ($\ge 2$ major exams, projects, or papers due within a 48-hour window).
* **Sunday Evening Weekly Planning Digest**
  * Deliver a comprehensive weekly overview every Sunday at 6:00 PM.
  * Include current grade standings across all courses, upcoming 7-day deadline timeline, and prominent workload clumping warning banners.

---

## Phase 3: Attendance Sentinel & Customization

Focus: Expand oversight into daily attendance anomalies and provide granular family configuration.

### Features
* **Attendance Anomaly Alerts**
  * Monitor period-level attendance records daily.
  * Dispatch alerts for unexcused absences, tardies, unverified absences, or cuts.
* **Customizable Thresholds & Grace Periods**
  * Allow families to configure custom grade drop trigger percentages (e.g., $3\%$ vs $5\%$) and custom grace period durations (e.g., 24h vs 48h).
* **Multi-Student Oversight**
  * Support monitoring multiple siblings or observees in a single unified notification feed.
