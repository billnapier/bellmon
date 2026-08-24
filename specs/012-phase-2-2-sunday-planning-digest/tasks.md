# Implementation Tasks: 012 Phase 2.2 Sunday Planning Digest

## Task List

- [x] **Task 1: Define Sunday Digest Payload Model** (`src/notifications/digest.py`)
  - Define `SundayDigestPayload` Pydantic schema with course standings, workload radar, deadlines, and attendance summary.
- [x] **Task 2: Implement Sunday Digest HTML & Text Renderer** (`src/notifications/digest.py`)
  - Create `SundayDigestRenderer` with `render_html()` and `render_text()`, implementing responsive styling and conditional radar warning banners.
- [x] **Task 3: Implement Sunday Digest Router & Schedule Validation** (`src/notifications/digest.py`)
  - Create `SundayDigestRouter` with `should_send_digest(now, last_sent_at)` checking Sunday >= 18:00 UTC and 48-hour deduplication window.
- [x] **Task 4: Export Digest Interfaces in Notification Package** (`src/notifications/__init__.py`)
  - Export `SundayDigestPayload`, `SundayDigestRenderer`, and `SundayDigestRouter`.
- [x] **Task 5: Write Comprehensive Unit Tests** (`tests/test_sunday_digest.py`)
  - Test HTML/Text compilation, conditional radar banner rendering, schedule window validation, and 48-hour deduplication logic.

