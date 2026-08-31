# Implementation Tasks: Phase 1.7 Late Submission Frequency Warning & Digest Integration

## Task Dependency Graph

```
Task 1: Core Models & Storage Ledger Updates
    |
    v
Task 2: Late Submission Sentinel Engine
    |
    v
Task 3: Sunday Digest Integration & Template Rendering
    |
    v
Task 4: Unit Testing & Validation
```

---

## Tasks Breakdown

### Task 1: Core Models & Storage Ledger Updates
**File(s)**: `src/storage/models.py`, `src/engine/models.py`, `src/storage/firestore.py`

- [x] Add `DispatchedAlertRecord` model to `src/storage/models.py`.
- [x] Add `LateSubmissionPatternAlert` model to `src/engine/models.py`.
- [x] Implement `save_dispatched_alert` and `get_dispatched_alerts` methods in `FirestoreStateEngine` (`src/storage/firestore.py`).
- [x] Support `dispatched_alerts` collection in `MockFirestoreClient` and live Firestore engine.

---

### Task 2: Late Submission Sentinel Engine
**File(s)**: `src/engine/late_submissions.py`, `src/engine/__init__.py`

- [x] Create `LateSubmissionSentinel` class in `src/engine/late_submissions.py`.
- [x] Implement `evaluate_late_submissions` method:
  - Filter `LateSubmissionRecord` items within rolling 7-day window `[now - 7 days, now]`.
  - Exclude minor latencies (`minutes_late < min_minutes_late`, default 5).
  - Count qualifying late submissions ($\ge 3$ threshold).
  - Check 7-day cooldown (168h) against `dispatched_alerts` history to suppress duplicate warnings.
  - Return `Tuple[Optional[LateSubmissionPatternAlert], List[LateSubmissionRecord]]`.
- [x] Re-export sentinel and models in `src/engine/__init__.py`.

---

### Task 3: Sunday Digest Integration & Template Rendering
**File(s)**: `src/notifications/digest.py`

- [x] Extend `SundayDigestPayload` model with `late_submissions: List[Dict[str, Any]]`, `late_count: int`, and `has_late_warning: bool`.
- [x] Update `SundayDigestRenderer.render_html` to render `⏱️ Late Submission Summary` section with details (Course, Assignment, Delay, Timestamp).
- [x] Add `⚠️ Late Submission Pattern Alert` warning banner to HTML when `has_late_warning` is true.
- [x] Update `SundayDigestRenderer.render_text` to include plain-text version of late submission summary and pattern warning.

---

### Task 4: Unit Testing & Validation
**File(s)**: `tests/unit/test_late_submissions.py`, `tests/unit/test_sunday_digest.py`

- [x] Create `tests/unit/test_late_submissions.py` testing:
  - Noise threshold filtering (<5 min excluded, >=5 min included).
  - Frequency trigger (2 late -> no alert, 3 late -> P1 alert).
  - Windowing logic (8-day-old submission excluded).
  - Alert ledger deduplication cooldown (suppressed if warning sent < 7 days ago).
- [x] Update `tests/unit/test_sunday_digest.py` testing:
  - HTML & Text rendering with 0 late submissions (section hidden or clean).
  - HTML & Text rendering with 2 late submissions (summary shown, warning banner hidden).
  - HTML & Text rendering with 3 late submissions (summary shown + warning banner active).
- [x] Run full test suite (`pytest tests/`) and confirm all tests pass cleanly.

