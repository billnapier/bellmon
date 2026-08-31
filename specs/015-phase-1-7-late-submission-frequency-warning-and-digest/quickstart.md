# Phase 1.7 Quickstart Guide

## 1. Unit Testing Late Submission Sentinel

Run pytest on the new sentinel unit tests:
```bash
pytest tests/unit/test_late_submissions.py -v
```

### Key Verification Cases
1. **Noise Thresholding**: Submissions late by 2 minutes are filtered out when `min_minutes_late=5`.
2. **Frequency Threshold**: 2 qualifying late submissions do NOT trigger a P1 alert; 3 qualifying late submissions DO trigger a P1 alert.
3. **Rolling Window**: Submissions outside the 7-day window (e.g. 8 days old) are excluded from the count.
4. **Deduplication Cooldown**: Second alert within 7 days is suppressed if an alert was previously logged in `dispatched_alerts`.

---

## 2. Testing Sunday Digest Late Submission Rendering

Run pytest on Sunday Digest rendering tests:
```bash
pytest tests/unit/test_sunday_digest.py -v
```

### Verification Checklist
- [ ] Digest HTML contains `⏱️ Late Submission Summary` section when late submissions are present.
- [ ] Digest HTML renders individual items showing Course Name, Assignment Title, formatted delay (e.g. `45 min late`), and timestamp.
- [ ] Digest HTML displays `⚠️ Late Submission Pattern Alert` warning banner when `has_late_warning` is `True` (or count $\ge 3$).
- [ ] Digest Plain Text version properly formats late submission entries and warning banner.

---

## 3. Integrated Test Suite Execution

Run the complete unit test suite:
```bash
pytest tests/ -v
```
