# Feature Specification: 012 Phase 2.2 Sunday Planning Digest

**Feature ID**: `012-phase-2-2-sunday-planning-digest`  
**Phase**: Phase 2.2 (Workload Radar & Sunday Digest)  
**Status**: Approved  

---

## 1. Executive Summary & Value Proposition

The **Sunday Evening Weekly Planning Digest** delivers a comprehensive, structured weekly email to parents every Sunday at 6:00 PM. It consolidates all current academic standings, upcoming 7-day deadlines, workload clumping warning banners, and weekly attendance tardy/unverified summaries into a single responsive HTML email. This eliminates Sunday-night surprises and empowers families to plan for the week ahead.

---

## 2. Requirements & Business Rules

### 2.1 Digest Payload Composition
The Sunday Planning Digest consolidates data from four primary sources:
1. **Course Standings**: Current letter grade, percentage, and teacher name for all active courses harvested from PowerSchool.
2. **7-Day Deadline Timeline**: Chronological list of all assignments, quizzes, and exams due over the upcoming week $[t_{\text{Sunday}}, t_{\text{Sunday}} + 7\text{ days}]$.
3. **Workload Clumping Radar Banners**: High-visibility alert banners rendered when `WorkloadRadarResult.has_clumping` is True.
4. **Weekly Attendance Summary**: Tardy (`T`) and Unverified (`U`) attendance records logged during the preceding 7 days.

### 2.2 Dispatch Schedule & Trigger Verification
1. **Schedule**: Triggered during the Sunday 6:00 PM Cloud Run batch execution run.
2. **Deduplication Ledger**: Records dispatch timestamp in Firestore (`digest_last_sent_at`) to prevent duplicate dispatches within a 48-hour window.

### 2.3 Email Rendering & Templates
1. **HTML & Plaintext Templates**: Both rich responsive HTML and plain text alternatives must be generated.
2. **Visual Hierarchy**:
   - Header: Bellmon Weekly Digest banner with student name and date.
   - Section 1: Workload Clumping Radar Warning (if active).
   - Section 2: Current Grade Standings table.
   - Section 3: Upcoming 7-Day Deadline Timeline.
   - Section 4: Weekly Attendance & Tardy Summary.

---

## 3. User Stories & Acceptance Criteria

### User Story 1: Render Complete Weekly Digest
- **Given** valid student grade, deadline, workload radar, and attendance data, **When** `render_sunday_digest()` is called, **Then** it generates clean HTML and plaintext email strings containing all four sections.

### User Story 2: Suppress Empty Radar Banners
- **Given** no workload clumping detected (`has_clumping == False`), **Then** the workload warning banner section is omitted from the rendered email.

---

## 4. Technical Specifications

### Components
- `src/notifications/digest.py`: `SundayDigestRenderer` and `SundayDigestRouter`.
- `tests/test_sunday_digest.py`: Unit tests for digest rendering and router scheduling rules.
