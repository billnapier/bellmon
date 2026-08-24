# Feature Specification: Phase 1.3 Grade Velocity Drop ($\ge 4.0\%$) Sentinel & Silent Warming Tracker

**Feature Branch**: `008-phase-1-3-grade-velocity-sentinel`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Phase 1.3 Grade Velocity drop evaluation engine ($\ge 4.0\%$), noise suppression filter, and silent warming protocol

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rolling Grade Velocity Drop Detection (Priority: P1)

As a parent, I want to receive urgent alerts when a student's course grade drops by $\ge 4.0\%$ compared to a historical snapshot from $[t-10, t-7]$ days ago so that rapid academic trajectory declines are flagged before report cards are issued.

**Why this priority**: Catches sudden drops in performance early (e.g. poor exam score or major project grade) rather than reacting to end-of-term overall grades.

**Independent Test**: Providing a current course percentage of 88.0% and a 7-day prior snapshot of 93.0% (delta = 5.0%) generates a `PendingGradeDropAlert`.

**Acceptance Scenarios**:

1. **Given** a current course grade of 88.0% and a historical snapshot of 93.0% in the $[t-10, t-7]$ day window, **When** evaluated, **Then** delta $\Delta = 5.0\% \ge 4.0\%$ triggers a pending grade velocity drop alert.
2. **Given** a current grade of 91.0% and a historical snapshot of 93.5% (delta = 2.5%), **When** evaluated, **Then** no alert is generated.

---

### User Story 2 - Early-Term Noise Suppression (Priority: P1)

As a student and parent, I want grade velocity drop alerts suppressed when a course has fewer than 100 total graded points AND the current term has been active for fewer than 21 calendar days (3 weeks) so that early-term grade volatility does not cause false alarms.

**Why this priority**: Single early assignments (e.g. 9/10 vs 10/10) cause extreme percentage swings that do not reflect actual academic risk.

**Independent Test**: Testing a 10.0% grade drop on a course with only 40 graded points and 14 term days active results in alert suppression.

**Acceptance Scenarios**:

1. **Given** a grade drop $\ge 4.0\%$ in a course with $< 100$ total graded points AND term length $< 21$ days, **When** evaluated, **Then** the velocity drop alert is suppressed.
2. **Given** a grade drop $\ge 4.0\%$ in a course with 150 graded points OR 25 term days active, **When** evaluated, **Then** the velocity drop alert is generated.

---

### User Story 3 - Silent Warming Protocol (Priority: P2)

As a system operator, I want velocity drop alerts silently suppressed during the initial 7 calendar days of deployment while grade history snapshots accumulate so that missing historical baselines do not trigger invalid alerts.

**Why this priority**: Prevents false alert generation during system initialization when historical data points do not yet exist.

**Independent Test**: Evaluating a student document created 3 days ago yields zero grade drop alerts even if grade snapshot changes occur.

**Acceptance Scenarios**:

1. **Given** a student profile with less than 7 calendar days of historical data in Firestore, **When** evaluated, **Then** grade history accumulates silently and velocity drop alerts are suppressed.

---

### Edge Cases

- What happens if no historical snapshot exists in the exact $[t-10, t-7]$ day window?
  - Selects the closest available historical snapshot within the maximum 14-day history window. If no snapshot exists $\ge 7$ days prior, evaluation is deferred.
- Does the grade drop alert specify which specific assignment caused the drop?
  - No. Per product requirements, the payload contains Course Name, Previous Grade %, Current Grade %, and Delta % to keep alerts clean and unambiguous.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `GradeVelocityEngine` in `src/engine/velocity.py`.
- **FR-002**: System MUST query Firestore grade history snapshots within a $[t-10, t-7]$ day window for each course.
- **FR-003**: System MUST calculate grade velocity drop delta: $\Delta = \text{percentage}_{t-\text{prev}} - \text{percentage}_{t-\text{curr}}$.
- **FR-004**: System MUST trigger an alert payload when $\Delta \ge 4.0\%$.
- **FR-005**: System MUST enforce noise suppression criteria: suppress alerts unless course total graded points $\ge 100$ OR term duration active $\ge 21$ calendar days.
- **FR-006**: System MUST enforce silent warming protocol: suppress alerts if total student tracking history is $< 7$ calendar days.
- **FR-007**: System MUST output structured `PendingGradeDropAlert` objects containing course name, previous percentage, current percentage, and delta.

### Key Entities

- **GradeSnapshot**: Object storing `date`, `percentage`, and `letter_grade`.
- **PendingGradeDropAlert**: Object storing `course_id`, `course_name`, `prev_percentage`, `curr_percentage`, `delta`, and `detected_at`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Grade velocity drop calculation correctly identifies deltas $\ge 4.0\%$ across historical windows in 100% of test cases.
- **SC-002**: 100% of volatile grade drops occurring under 100 graded points and 21 term days are suppressed.
- **SC-003**: Zero false alerts are emitted during the initial 7-day silent warming period.
