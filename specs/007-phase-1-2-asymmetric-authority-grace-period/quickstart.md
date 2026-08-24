# Quickstart & Testing Guide: Phase 1.2

## Running Unit Tests

Execute `pytest` to run all unit tests for the Asymmetric Authority Engine:

```bash
pytest tests/test_authority.py -v
```

## Key Test Scenarios Covered

1. **Digital Canvas Missing Initialization**: Missing Canvas upload assignment initializes state to `GRACE_PERIOD`.
2. **Weekend Blackout Calculation**: Verification that hours between Friday 5:00 PM and Monday 8:00 AM are excluded from the 36-hour grace period budget.
3. **Grace Period Expiration**: 36 active weekday hours elapsing changes status to `EXPIRED` and generates a `CANVAS_GRACE_EXPIRED` alert payload.
4. **Grace Period Resolution**: Student submitting before 36 hours clears state to `RESOLVED` with zero alert.
5. **PowerSchool Confirmed Missing**: PowerSchool item with `isMissing: true` or `score: 0` immediately triggers `CONFIRMED_MISSING` and `POWERSCHOOL_CONFIRMED` alert.
6. **Paper Work Suppression**: Canvas missing item with `submission_types: ['on_paper']` or `['none']` transitions to `SUPPRESSED` with zero alert.
