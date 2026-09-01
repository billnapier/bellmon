# Technical Plan: 013 Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

## Module Structure

```
src/
├── main.py                          # Updated with Sunday batch execution orchestration
├── notifications/
│   ├── digest.py                    # SundayDigestPayload, SundayDigestRenderer, SundayDigestRouter
│   └── resend.py                    # ResendClient email delivery
└── radar/
    └── engine.py                    # WorkloadRadarEngine
tests/
└── test_sunday_batch_integration.py # Integration test suite for Sunday batch orchestration
```

## Technical Specifications

### `SundayBatchExecutionLog`
- Structured telemetry model emitted during Sunday runs.

### `main.py` Updates
- `run_batch(student_id, canvas_client, powerschool_scraper, force_sunday, now_override)`:
  - Executes Canvas and PowerSchool ingestion.
  - Checks if `SundayDigestRouter.should_send_digest(now)` returns True (or `force_sunday=True`).
  - If Sunday run:
    - Runs `WorkloadRadarEngine.evaluate()`.
    - Assembles `SundayDigestPayload`.
    - Renders digest via `SundayDigestRenderer`.
    - Dispatches email via `ResendClient` / `NotificationRouter`.
    - Prints `SundayBatchExecutionLog` JSON telemetry record to stdout.

## Key Test Scenarios
1. **Sunday Trigger Execution**: Executing batch run when `is_sunday=True` triggers radar evaluation and digest dispatch via Resend.
2. **Weekday Non-Trigger**: Executing batch run on a non-Sunday skips digest dispatch.
3. **Ingestion Fallback**: When ingestion fails, fallback to cached Firestore state is used for digest generation without raising an uncaught exception.
4. **Structured Logging**: Verify `SundayBatchExecutionLog` is emitted as standard JSON stdout.
