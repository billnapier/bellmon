# Data Model: Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

## Models

### `SundayBatchExecutionLog`

Telemetry data model emitted to standard output during Sunday batch runs for observability and Cloud Run log ingestion.

```python
class SundayBatchExecutionLog(BaseModel):
    timestamp: str
    is_sunday_run: bool
    radar_clumping_found: bool
    digest_dispatched: bool
    resend_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
```

## Existing Integrated Models

- `StudentSnapshot` (from `src.main`)
- `BatchExecutionResult` (from `src.main`)
- `WorkloadRadarResult` (from `src.radar.models`)
- `SundayDigestPayload` (from `src.notifications.digest`)
- `DispatchResult` (from `src.notifications.models`)
