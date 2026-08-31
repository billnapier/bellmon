# Research: Phase 1.6 Canvas Late Submission Tracking

## 1. Canvas Submission API & Late Field Ingestion

### Decision
Extend `CanvasClient` in `src/ingestion/canvas.py` to parse `CanvasSubmission` payload items containing:
- `id` / `assignment_id`
- `late` (boolean)
- `submitted_at` (ISO timestamp string or datetime)
- `due_at` (ISO timestamp string or datetime)
- `course_id` & `assignment` metadata (`title`/`name`)

### Rationale
Canvas API includes `late: true/false` directly in submission responses. Additionally, evaluating `submitted_at > due_at` catches submissions flagged manually or implicitly.

### Alternatives Considered
- Querying gradebook history: Too heavy and expensive.
- Polling missing submissions endpoint only: Doesn't catch assignments that were submitted late (since once submitted, they are no longer in `missing_submissions`).

---

## 2. Firestore Document Structure & Idempotency

### Decision
Store each late submission as an individual document in Firestore under subcollection:
`students/{student_id}/late_submissions/{assignment_id}`

### Rationale
- Using `{assignment_id}` as document ID ensures idempotent updates during repeated syncs.
- Allows targeted queries using start/end date filters on `submitted_at` or `detected_at`.

---

## 3. Edge Case Handling

- **Missing `submitted_at` but `late == True`**: Use detection execution timestamp `detected_at` to compute approximate late duration.
- **Teacher due date extension**: Re-evaluating an existing assignment checks if `submitted_at <= updated_due_at`. If so, `is_late` is set to `False` and `minutes_late` is updated to `0`.
