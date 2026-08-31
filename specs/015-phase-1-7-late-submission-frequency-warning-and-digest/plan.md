# Feature Plan: Phase 1.7 Late Submission Frequency Warning & Digest Integration

## Executive Summary
This document outlines the architecture, implementation strategy, and testing workflow for **Phase 1.7 Late Submission Frequency Warning & Digest Integration** (Feature 015).

---

## Technical Architecture & Blueprint

```
+------------------------------------+
|  Harvested Canvas Late Submissions |
+------------------------------------+
                  |
                  v
+------------------------------------+
|     LateSubmissionSentinel         |
|  - Filter window [now-7d, now]     |
|  - Filter minutes_late >= 5        |
|  - Check frequency threshold >= 3  |
+------------------------------------+
                  |
                  v
+------------------------------------+      +--------------------------------+
|      Deduplication Check           | ---> |  Firestore Dispatched Alerts   |
|  - Suppress if alert sent in < 7d  |      |  students/{id}/dispatched_alerts|
+------------------------------------+      +--------------------------------+
                  |
                  +-----------------------------------+
                  |                                   |
                  v                                   v
+------------------------------------+   +-----------------------------------+
|  Standalone P1 Warning Email Alert |   |   Sunday Evening Digest Integration |
|  - Triggered immediately if count  |   |   - Includes 7-day late summary   |
|    >= 3 and outside 7-day cooldown |   |   - Highlights chronic pattern    |
+------------------------------------+   +-----------------------------------+
```

---

## Key Modules & Components

1. **Storage Models (`src/storage/models.py`)**:
   - `DispatchedAlertRecord`: Model representing historical dispatched alerts for deduplication checks.

2. **Engine Models (`src/engine/models.py`)**:
   - `LateSubmissionPatternAlert`: Alert structure for P1 frequency warnings.

3. **Firestore Engine (`src/storage/firestore.py`)**:
   - `save_dispatched_alert(student_id, record)`: Idempotently save alert record to `students/{student_id}/dispatched_alerts/{alert_id}`.
   - `get_dispatched_alerts(student_id, alert_type, start_date, end_date)`: Retrieve dispatched alert history.

4. **Late Submission Sentinel Engine (`src/engine/late_submissions.py`)**:
   - `LateSubmissionSentinel`: Business logic for window filtering, noise filtering (`min_minutes_late`), frequency counting, and alert cooldown evaluation.

5. **Sunday Digest Engine (`src/notifications/digest.py`)**:
   - Extend `SundayDigestPayload` with `late_submissions`, `late_count`, and `has_late_warning`.
   - Update `SundayDigestRenderer` HTML and text formatting methods to include Late Submission Summary and Pattern Warning Banner.

---

## Phase Execution Checklist

- [ ] **Data & Storage Foundation**: Update models and Firestore engine to persist and retrieve dispatched alert records.
- [ ] **Sentinel Logic Implementation**: Implement `LateSubmissionSentinel` with 7-day window filtering, noise filtering, and 7-day cooldown.
- [ ] **Sunday Digest Extension**: Update `SundayDigestPayload` and `SundayDigestRenderer` with late submission sections and warning alerts.
- [ ] **Testing**: Create comprehensive unit tests verifying noise filtering, frequency thresholds, rolling windows, deduplication, and email template rendering.
