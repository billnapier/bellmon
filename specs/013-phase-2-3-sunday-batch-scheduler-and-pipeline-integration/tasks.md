# Implementation Tasks: 013 Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

## Task List

- [x] **Task 1: Define Sunday Batch Telemetry Model** (`src/main.py`)
  - Define `SundayBatchExecutionLog` Pydantic model for structured JSON output logging.
- [x] **Task 2: Integrate Sunday Batch Execution in `main.py`** (`src/main.py`)
  - Update `run_batch()` to evaluate `SundayDigestRouter.should_send_digest()`, invoke `WorkloadRadarEngine`, assemble `SundayDigestPayload`, render digest HTML/text, dispatch via `ResendClient`, and emit `SundayBatchExecutionLog`.
- [x] **Task 3: Implement Ingestion Failure Fallback Logic** (`src/main.py`)
  - Add fallback logic to read cached student snapshot state if Canvas/PowerSchool ingestion fails during a Sunday execution run.
- [x] **Task 4: Write Integration Tests for Sunday Batch Execution** (`tests/test_sunday_batch_integration.py`)
  - Create integration test suite verifying Sunday batch orchestration, non-Sunday skipping, Resend dispatching, and fallback handling.
- [x] **Task 5: Update Spec Status Dashboard** (`specs/STATUS.md`)
  - Update `specs/STATUS.md` to reflect Feature 013 status as 100% complete.
