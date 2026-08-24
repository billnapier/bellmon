# Technical Research: 012 Phase 2.2 Sunday Planning Digest

## 1. Objective & Scope
Research the requirements, schedule check logic, and data aggregation workflow for generating and routing the Sunday Evening 6:00 PM Weekly Planning Digest email.

## 2. Schedule Check Logic
- The runner executes every hour or on batch schedule.
- `is_sunday_digest_time(now)` returns `True` iff `now.weekday() == 6` (Sunday) and `now.hour >= 18`.
- Firestore deduplication ledger: `digest_last_sent_at` timestamp stored on student record. If sent within the past 48 hours, skip dispatch to prevent duplicate weekly emails.

## 3. Email Section Aggregation & Layout
1. **Header**: Bellmon Weekly Digest banner, student name, time period.
2. **Workload Clumping Radar Banner**: Displayed prominently if `WorkloadRadarResult.has_clumping` is True, detailing cluster dates and courses involved.
3. **Current Grade Standings**: HTML table of all courses, current grade (letter + percentage), teacher name.
4. **Upcoming 7-Day Deadline Timeline**: Chronological list of assignments/exams due in the upcoming week.
5. **Weekly Attendance Summary**: Count and breakdown of Tardy (`T`) and Unverified (`U`) attendance occurrences over the preceding 7 days.
