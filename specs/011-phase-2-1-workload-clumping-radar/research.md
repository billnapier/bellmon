# Technical Research: 011 Phase 2.1 Workload Clumping Radar

## 1. Objective & Scope
Research algorithms and criteria for detecting academic workload clumping ($\ge 2$ major assessments due within a rolling 48-hour window over a 7-day horizon) without generating excessive noise from daily homework.

## 2. Assessment Classification Heuristics
- **Keyword Patterns**:
  - `Exam`, `Test`, `Midterm`, `Final`, `Quiz` (if $\ge 50$ pts), `Project`, `Paper`, `Essay`, `Presentation`, `Lab`.
- **Point Threshold**:
  - `points_possible >= 50.0`.
- **Exclusion Filters**:
  - Submitted assignments (`has_submitted_submissions == True` or valid `submitted_at`).
  - Past due dates (`due_at < now`).
  - Out of range due dates (`due_at > now + 7 days`).

## 3. Rolling 48-Hour Window Clustering Algorithm
- **Input**: Sorted list of active major assessments ordered by `due_at`.
- **Algorithm**:
  1. Maintain active cluster list.
  2. For each assessment `A`:
     - Find existing cluster `C` where `A.due_at - C.start_time <= 48 hours` or `A.due_at - C.end_time <= 48 hours`.
     - If found, append `A` to `C` and update `C.end_time = max(C.end_time, A.due_at)`.
     - Else, start new potential cluster candidate with `A`.
  3. Filter cluster candidates to those containing $\ge 2$ assessments.
- **Output**: List of valid `WorkloadCluster` objects.
