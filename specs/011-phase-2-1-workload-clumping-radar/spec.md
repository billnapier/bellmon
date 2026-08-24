# Feature Specification: 011 Phase 2.1 Workload Clumping Radar

**Feature ID**: `011-phase-2-1-workload-clumping-radar`  
**Phase**: Phase 2.1 (Workload Radar & Sunday Digest)  
**Status**: Approved  

---

## 1. Executive Summary & Value Proposition

High school students often face severe academic stress when multiple high-stakes exams, papers, or major projects coincide within a tight 48-hour window. The **Workload Clumping Radar** analyzes upcoming assignment and exam schedules over a 7-day forward horizon, automatically detecting clusters of major assessments ($\ge 2$ major items within any 48-hour window). This provides families with advance warning to plan study schedules and avoid Sunday-night emergencies.

---

## 2. Requirements & Business Rules

### 2.1 Major Assessment Classification
An assignment or calendar item is classified as a **Major Assessment** if it satisfies *either* of the following conditions:
1. **Category Match**: The assignment category, group name, or title contains any of the case-insensitive keywords: `Exam`, `Test`, `Project`, `Midterm`, `Final`, `Paper`, `Essay`, `Presentation`.
2. **High Point Weight**: The assignment's `points_possible` value is $\ge 50.0$.

### 2.2 Forward Time Horizon & Window Evaluation
1. **Time Horizon**: Scan items with `due_at` timestamps occurring within $[t_{\text{now}}, t_{\text{now}} + 7\text{ days}]$.
2. **Rolling 48-Hour Window**: Identify any subset of $\ge 2$ major assessments whose due dates fall within a 48-hour time difference ($|t_{\text{due, B}} - t_{\text{due, A}}| \le 48\text{ hours}$).
3. **Cluster Aggregation**: Overlapping or adjacent 48-hour windows containing shared assessments are aggregated into a single `WorkloadCluster`.

### 2.3 Noise Suppression & Status Filtering
1. **Already Submitted**: Assignments marked as submitted (`has_submitted_submissions == True` or non-null submission timestamp) are excluded from active workload clumping.
2. **Past Items**: Items with `due_at` prior to $t_{\text{now}}$ are ignored.

### 2.4 Data Output Schema
The engine produces structured `WorkloadRadarResult` payloads containing:
* `has_clumping`: Boolean flag indicating if any workload clusters were detected.
* `clusters`: List of `WorkloadCluster` models, each specifying:
  * `start_time`: ISO8601 string of earliest assessment in cluster.
  * `end_time`: ISO8601 string of latest assessment in cluster.
  * `courses`: List of unique course names involved in the cluster.
  * `assessments`: List of `AssessmentSummary` objects (title, course_name, due_at, points_possible, category).

---

## 3. User Stories & Acceptance Criteria

### User Story 1: Identify Major Assessments
*As a monitoring engine, I want to accurately classify assignments as major vs routine tasks so that minor daily homework items do not trigger false workload alarms.*
- **Given** an assignment with title "Unit 3 Chemistry Exam" (points: 20), **Then** it is classified as a Major Assessment due to keyword match.
- **Given** an assignment with title "Lab Report 1" (points: 50.0), **Then** it is classified as a Major Assessment due to point threshold $\ge 50$.
- **Given** a daily homework assignment "Page 42 #1-10" (points: 10.0), **Then** it is NOT classified as a Major Assessment.

### User Story 2: Detect 48-Hour Clumping
*As a parent, I want to be alerted when 2 or more major exams/projects occur within 48 hours so we can plan ahead.*
- **Given** two major exams scheduled within 24 hours of each other in the upcoming 7 days, **Then** the engine groups them into a `WorkloadCluster`.
- **Given** three major projects due on Tuesday 9 AM, Wednesday 2 PM, and Thursday 11 AM, **Then** all three are aggregated into a single cluster spanning Tuesday to Thursday.
- **Given** two major exams scheduled 72 hours apart, **Then** no workload cluster is flagged.

---

## 4. Technical Specifications & Architecture

### Components
- `src/radar/models.py`: Pydantic schemas (`AssessmentSummary`, `WorkloadCluster`, `WorkloadRadarResult`).
- `src/radar/engine.py`: `WorkloadRadarEngine` implementing classification and rolling window clustering algorithms.
- `tests/test_workload_radar.py`: Comprehensive test suite verifying edge cases, multi-course clumping, and threshold boundaries.
