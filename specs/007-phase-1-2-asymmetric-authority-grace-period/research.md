# Phase 0 Research: Asymmetric System Authority & Weekend-Aware Grace Period Logic

## Overview

Feature 007 establishes the core business rules for evaluating assignment statuses reported by Canvas LMS and PowerSchool SIS.

## Key Research Decisions

### 1. Weekend Window & Grace Period Calculation Strategy

- **Requirement**: A 36-calendar-hour grace period for digital Canvas assignments (`online_upload`). The timer pauses on weekends from Friday 17:00:00 (5:00 PM) to Monday 08:00:00 (8:00 AM) local time.
- **Decision**: Implement a deterministic datetime math helper `calculate_elapsed_weekday_hours(start_dt: datetime, end_dt: datetime, tz_name: str = "America/Los_Angeles") -> float`.
- **Rationale**: Iterating or clipping date ranges hour-by-hour (or segment-by-segment) within `start_dt` to `end_dt` accurately subtracts weekend blackout hours without rounding errors or timezone bugs.
- **Alternatives Considered**: 
  - Simple `(end_dt - start_dt).total_seconds() / 3600`: Fails to exclude weekend blackout hours.
  - Hardcoded hour subtraction: Error-prone across multiple weekend boundaries or arbitrary detection times.

### 2. Status Enums & State Machine

- **Decision**: Define `AssignmentStatus(str, Enum)` with values:
  - `NEW`: Assignment first observed, not yet evaluated.
  - `GRACE_PERIOD`: Canvas digital missing assignment within 36 weekday hours.
  - `EXPIRED`: Grace period elapsed without student submission; queued for P0 alert (`CANVAS_GRACE_EXPIRED`).
  - `CONFIRMED_MISSING`: PowerSchool item marked `isMissing: true` or `score: 0`; queued for P0 alert (`POWERSCHOOL_CONFIRMED`).
  - `RESOLVED`: Student submitted work or grade updated; zero alert dispatched.
  - `SUPPRESSED`: Canvas missing assignment with submission types `['on_paper']` or `['none']`.
- **Rationale**: Explicit state machine prevents ambiguous state transitions and provides clean auditability in Firestore.

### 3. Pure Asymmetric Authority Model (No Cross-System Title Matching)

- **Decision**: Process Canvas items and PowerSchool items in separate tracking pipelines without fuzzy-string matching titles across systems.
- **Rationale**: Gradebook title mismatches between Canvas and PowerSchool (e.g. "HW 3" vs "Homework #3 - Ch 4") caused false positives in initial system designs. Under the asymmetric authority model:
  - Canvas handles digital submission grace periods independently.
  - PowerSchool handles official district gradebook confirmed zeros independently.
  - Non-digital Canvas items (`on_paper`, `none`) are suppressed entirely to avoid double-alerting.
