# Technical Research: Phase 1.9 Daily Evening Homework & Deadline Snapshot

## Research Findings & Architectural Decisions

### 1. Forward-Looking Window Querying [24-48 Hours]
- **Decision**: Query assignments with `due_at` timestamp in range `[snapshot_time, snapshot_time + 48 hours]`.
- **Rationale**: 7:00 PM evening runs provide students and parents a clear view of homework due tonight (e.g. 11:59 PM), tomorrow, and up to 48 hours out.
- **Alternatives Considered**: Querying fixed calendar days (e.g., today/tomorrow). Rolling 48 hours handles variable assignment due times more accurately.

### 2. Grace Period Escalation Callout
- **Decision**: Query assignments in `GRACE_PERIOD` state for the student and render a prominent red alert section.
- **Rationale**: Directs evening focus to assignments closest to expiration before triggering P0 missing work alerts. Includes direct Canvas/PowerSchool submission links.

### 3. Asymmetric Authority Handling
- **Decision**: If Canvas status is `submitted`, mark assignment as `Submitted` even if PowerSchool lists missing.
- **Rationale**: Standard system rule: Canvas is authority for submission evidence.

### 4. Idempotency & Resend Routing
- **Decision**: Use `homework_snapshots` Firestore collection with key `student_id:YYYY-MM-DD`. Route dispatches through `ResendNotificationRouter`.
- **Rationale**: Matches existing daily briefing pattern (`sunday_digests`, `heartbeat_briefings`), guaranteeing max 1 dispatch per day per student.
