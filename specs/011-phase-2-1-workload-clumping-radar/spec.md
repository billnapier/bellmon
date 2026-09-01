# Feature Specification: Phase 2.1 Workload Clumping Radar

**Feature Branch**: `011-phase-2-1-workload-clumping-radar`  
**Created**: 2026-08-31  
**Status**: Draft  
**Input**: 7-day forward horizon assignment/exam schedule scanner detecting major assessment clusters ($\ge 2$ major items within any 48-hour window) to eliminate Sunday-night study emergencies (PRD §4.4, CUJ-6)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Major Assessment Classification (Priority: P0)

As a monitoring engine, I want to accurately classify assignments as major assessments vs routine tasks so that minor daily homework assignments do not trigger false workload alarms.

**Why this priority**: Core prerequisite for preventing false positive workload warnings.

**Independent Test**: Running classification logic on an assignment titled "Unit 3 Chemistry Exam" (20 pts) flags it as a major assessment via keyword match, while a daily homework assignment "Page 42 #1-10" (10 pts) is classified as routine.

**Acceptance Scenarios**:

1. **Given** an assignment whose title, group, or category contains case-insensitive keywords `['Exam', 'Test', 'Project', 'Midterm', 'Final', 'Paper', 'Essay', 'Presentation']`, **When** evaluated by `WorkloadRadarEngine.is_major_assessment()`, **Then** it is classified as a Major Assessment (`is_major == True`).
2. **Given** an assignment with `points_possible >= 50.0`, **When** evaluated, **Then** it is classified as a Major Assessment regardless of title.
3. **Given** an assignment with `points_possible < 50.0` and no keyword match, **When** evaluated, **Then** it is NOT classified as a Major Assessment (`is_major == False`).

---

### User Story 2 - Rolling 48-Hour Clumping Detection (Priority: P0)

As a parent, I want to be alerted when 2 or more major exams, projects, or papers occur within a rolling 48-hour window over the next 7 days so that our family can prepare study schedules in advance.

**Why this priority**: High-stakes workload spikes require advance study planning to avoid last-minute stress.

**Independent Test**: Inputting two major exams due 24 hours apart within the 7-day forward window generates a `WorkloadCluster` listing both exams and affected courses.

**Acceptance Scenarios**:

1. **Given** 2 or more major assessments with due dates in $[t_{\text{now}}, t_{\text{now}} + 7\text{ days}]$ such that $|t_{\text{due, B}} - t_{\text{due, A}}| \le 48\text{ hours}$, **When** `WorkloadRadarEngine.analyze()` is called, **Then** a `WorkloadCluster` is generated containing both assessments.
2. **Given** 3 major items due on Tuesday 9:00 AM, Wednesday 2:00 PM, and Thursday 11:00 AM, **When** evaluated, **Then** all three are aggregated into a single continuous cluster spanning Tuesday to Thursday.
3. **Given** two major exams scheduled 72 hours apart, **When** evaluated, **Then** `has_clumping` is returned as `False` and zero clusters are flagged.

---

### User Story 3 - Submitted & Past Item Noise Filtering (Priority: P1)

As a parent, I want completed or past assignments excluded from workload radar calculations so that the radar reflects only pending upcoming study commitments.

**Why this priority**: Avoids alerting on workload clusters that the student has already completed or submitted.

**Independent Test**: Marking an assignment in a 2-exam cluster as `submitted` removes the cluster if fewer than 2 unsubmitted major assessments remain in the window.

**Acceptance Scenarios**:

1. **Given** an assignment with `has_submitted_submissions == True` or a non-null `submitted_at` timestamp, **When** analyzed, **Then** it is excluded from workload cluster evaluation.
2. **Given** an assignment with `due_at < t_{\text{now}}`, **When** analyzed, **Then** it is excluded from upcoming workload analysis.

---

### Edge Cases

- What if 4 major exams fall within the same 48-hour window across 4 different courses?
  - All 4 assessments are grouped into a single cluster with `courses` listing all 4 distinct course names.
- What if an assignment has missing or null `due_at` timestamp?
  - Items without valid `due_at` timestamps are excluded from clumping calculations and logged as warnings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `WorkloadRadarEngine` in `src/radar/engine.py`.
- **FR-002**: System MUST define Pydantic models `AssessmentSummary`, `WorkloadCluster`, and `WorkloadRadarResult` in `src/radar/models.py`.
- **FR-003**: System MUST classify assignments as major assessments using title keyword matching (`Exam`, `Test`, `Project`, `Midterm`, `Final`, `Paper`, `Essay`, `Presentation`) OR point threshold (`points_possible >= 50.0`).
- **FR-004**: System MUST scan items within the forward horizon $[t_{\text{now}}, t_{\text{now}} + 7\text{ days}]$.
- **FR-005**: System MUST aggregate any subset of $\ge 2$ unsubmitted major assessments within $|t_{\text{due, B}} - t_{\text{due, A}}| \le 48\text{ hours}$ into a `WorkloadCluster`.
- **FR-006**: System MUST filter out already submitted assignments (`has_submitted_submissions == True` or non-null `submitted_at`).

### Key Entities

- **AssessmentSummary**: `title` (str), `course_name` (str), `due_at` (str ISO8601), `points_possible` (float), `category` (str).
- **WorkloadCluster**: `start_time` (str ISO8601), `end_time` (str ISO8601), `courses` (List[str]), `assessments` (List[AssessmentSummary]).
- **WorkloadRadarResult**: `has_clumping` (bool), `clusters` (List[WorkloadCluster]), `analyzed_at` (str ISO8601).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of major assessment title keywords and $\ge 50$ point items are correctly classified.
- **SC-002**: 100% of 48-hour rolling windows with $\ge 2$ major unsubmitted assessments generate a valid `WorkloadCluster`.
- **SC-003**: Zero submitted or past assignments are included in active workload clumping clusters.
