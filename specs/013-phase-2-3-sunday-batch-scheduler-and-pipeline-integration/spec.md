# Feature Specification: Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

**Feature Branch**: `013-phase-2-3-sunday-batch-scheduler-and-pipeline-integration`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: End-to-end integration of `WorkloadRadarEngine` and `SundayDigestRouter` into the main batch execution runner (`main.py`) for Cloud Run scheduled execution (PRD §7.2, CUJ-6, CUJ-7)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sunday Scheduled Batch Execution Orchestration (Priority: P0)

As a system operator, I want the main batch execution job (`main.py`) to detect Sunday run triggers, execute the Workload Radar Engine, gather student state, and dispatch the Sunday Planning Digest seamlessly during the scheduled 6:00 PM Cloud Run run.

**Why this priority**: Orchestrates all Phase 2 components into a unified execution pipeline.

**Independent Test**: Executing `main.py` with mock system time set to Sunday 6:00 PM runs Canvas/PowerSchool ingestion, updates Firestore state, runs `WorkloadRadarEngine`, and dispatches the Sunday Digest via Resend.

**Acceptance Scenarios**:

1. **Given** the batch job executes on Sunday at 6:00 PM, **When** `main.py` completes data harvesting, **Then** `WorkloadRadarEngine.analyze()` is called using the 7-day forward horizon.
2. **Given** workload radar analysis completes, **When** `SundayDigestRouter.dispatch_if_due()` is called, **Then** the consolidated HTML/text digest payload is dispatched to registered parent emails.
3. **Given** the batch job executes on a weekday at 5:00 PM, **When** `main.py` executes, **Then** Sunday Digest generation is skipped while standard P0 alert checks run.

---

### User Story 2 - Resend Notification Router Integration (Priority: P0)

As a parent, I want the Sunday Digest delivered reliably using the Resend email provider with proper error handling and retry logging so that weekly updates are guaranteed.

**Why this priority**: Guarantees email delivery via the primary notification provider (Resend).

**Independent Test**: Mocking Resend API success dispatches the Sunday Digest email and updates the Firestore `digest_ledger` collection.

**Acceptance Scenarios**:

1. **Given** a generated `SundayDigestPayload`, **When** handed to `ResendNotificationRouter.send_digest()`, **Then** Resend API `/emails` endpoint is invoked with subject `"Bellmon Weekly Planning Digest - [Student Name]"`.
2. **Given** Resend API responds with an error, **When** caught by `SundayDigestRouter`, **Then** the failure is logged and Firestore ledger remains uncommitted to allow safe retry on the next execution cycle.

---

### User Story 3 - End-to-End Pipeline Logging & Status Monitoring (Priority: P1)

As a developer, I want detailed execution logs emitted during Sunday batch runs so that I can audit radar cluster detection, digest generation, and email dispatch status in Cloud Run logs.

**Why this priority**: Provides observability for batch executions in GCP Cloud Run.

**Independent Test**: Running the Sunday batch pipeline prints structured JSON logs indicating `ingestion_status`, `radar_clumping_detected`, `digest_rendered`, and `resend_message_id`.

**Acceptance Scenarios**:

1. **Given** a completed Sunday batch execution, **When** inspected in logs, **Then** structured log entries confirm each phase of execution (`harvest`, `radar`, `digest`, `dispatch`).

---

### Edge Cases

- What if data harvesting fails for PowerSchool on Sunday at 6:00 PM?
  - Sunday Digest generation proceeds using cached Firestore grade state with a prominent notice: "Grade data reflects last successful sync: [timestamp]".
- What if Cloud Scheduler triggers the run 5 minutes late (e.g. 6:05 PM)?
  - Schedule window matching allows a $\pm 30$-minute tolerance around 6:00 PM on Sunday.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST update `src/main.py` to integrate `WorkloadRadarEngine` and `SundayDigestRouter`.
- **FR-002**: System MUST evaluate day-of-week and time-of-day in `main.py` to determine whether Sunday Digest dispatch should be triggered ($\pm 30$ minutes of 6:00 PM Sunday).
- **FR-003**: System MUST fall back to cached Firestore state if live ingestion fails during Sunday digest rendering.
- **FR-004**: System MUST dispatch Sunday Digest emails via `ResendNotificationRouter`.
- **FR-005**: System MUST log structured JSON telemetry for Sunday batch execution events.

### Key Entities

- **SundayBatchExecutionLog**: `timestamp` (str), `is_sunday_run` (bool), `radar_clumping_found` (bool), `digest_dispatched` (bool), `resend_id` (Optional[str]), `errors` (List[str]).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Sunday 6:00 PM batch runs execute the full pipeline (harvest $\rightarrow$ radar $\rightarrow$ digest $\rightarrow$ dispatch).
- **SC-002**: Ingestion failures on Sunday fall back gracefully to cached Firestore state without aborting digest delivery.
- **SC-003**: Structured logs provide complete execution trace for 100% of Sunday runs.
