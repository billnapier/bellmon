# Quickstart Guide: Phase 2.3 Sunday Batch Scheduler & Pipeline Integration

## Overview

This feature integrates the Workload Clumping Radar (`WorkloadRadarEngine`) and Sunday Evening Digest (`SundayDigestRouter` & `SundayDigestRenderer`) into `src/main.py` for automated Cloud Run scheduled executions.

## Execution Example

### Triggering Sunday Batch Orchestration (Local Simulation)

```bash
# Run main.py with simulated Sunday environment variables
python -m src.main
```

### Running Unit Tests

```bash
pytest tests/test_sunday_batch_integration.py -v
```
