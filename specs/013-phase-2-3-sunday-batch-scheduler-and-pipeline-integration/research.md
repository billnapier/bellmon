# Research Document: Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

## Technical Context & Decisions

### 1. Ingestion Pipeline & Execution Trigger
- **Schedule Evaluation**: Cloud Run jobs execute on demand or via Cloud Scheduler (e.g. at 18:00 UTC every Sunday).
- **Time Window Heuristics**: To handle Cloud Scheduler skew or manual triggers around the schedule window, `should_send_digest()` or `main.py` evaluates if `now.weekday() == 6` (Sunday) and `now.hour >= 17` and `now.hour <= 19` (or `now.hour >= 18`).
- **Cached State Fallback**: If Canvas or PowerSchool ingestion fails during Sunday batch run, data harvesting status will be `PARTIAL_FAILURE` or `FAILURE`. In this event, `main.py` falls back to querying the cached student state from Firestore state persistence engine (`FirestoreStateEngine`) to render the digest, attaching a notice in log and payload.

### 2. Workload Radar & Sunday Digest Execution Sequence
1. Ingest Canvas assignments and PowerSchool grades/attendance (`run_batch`).
2. Persist updated student snapshot to Firestore (or read cached snapshot if ingestion fails).
3. If Sunday batch trigger is active:
   a. Instantiate `WorkloadRadarEngine` and run `evaluate()` over forward 7-day assignments horizon.
   b. Construct `SundayDigestPayload` aggregating:
      - Course standings (from Canvas/PowerSchool)
      - Workload radar results (from `WorkloadRadarEngine`)
      - Upcoming 7-day deadlines
      - Attendance summary (tardies / unverified absences)
      - Late submission summary (from `FirestoreStateEngine` / late submission tracker)
   c. Use `SundayDigestRenderer` to compile HTML/text bodies.
   d. Instantiate `ResendClient` (or `NotificationRouter`) to dispatch email to parent recipient(s).
   e. Log `SundayBatchExecutionLog` JSON telemetry record to stdout.

### 3. Verification & Observability
- Logging uses structured JSON format compatible with GCP Cloud Logging.
- Unit tests test batch execution with mock clients, verifying both Sunday execution path (with dispatch) and non-Sunday execution path (skip digest).
