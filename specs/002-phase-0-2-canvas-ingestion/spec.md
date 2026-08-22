# Feature Specification: Phase 0.2 Canvas LMS REST API Ingestion Module

**Feature Branch**: `002-phase-0-2-canvas-ingestion`  
**Created**: 2026-08-21  
**Status**: Draft  
**Input**: Phase 0.2 Canvas REST API ingestion module for course and assignment harvest

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Canvas API Data Harvesting (Priority: P1)

As an academic monitoring sentinel, I want to authenticate against the Canvas LMS REST API using a personal access token so that I can fetch a student observee's course enrollments, missing digital submissions, and assignment due dates.

**Why this priority**: Core Canvas data ingestion is required to detect overdue digital assignments and populate student snapshots.

**Independent Test**: Running the Canvas client module against the Canvas API (or mock response fixtures) successfully parses course lists and missing submission payloads into structured Python models.

**Acceptance Scenarios**:

1. **Given** a valid Canvas Personal Access Token, **When** the ingestion engine queries `GET /api/v1/users/:observee_id/missing_submissions`, **Then** it retrieves all overdue assignments with attributes `assignment_id`, `name`, `due_at`, `submission_types`, `points_possible`, and `has_submitted_submissions`.
2. **Given** course IDs associated with an observee, **When** querying `GET /api/v1/courses/:course_id/assignments`, **Then** it returns active course assignment lists.

---

### User Story 2 - Secure Secret Resolution (Priority: P1)

As a security-conscious application, I want the Canvas API access token to be resolved dynamically from GCP Secret Manager (with fallback to local environment variables) so that plain-text tokens are never stored in source code or configuration files.

**Why this priority**: Prevents credential leaks and complies with production security standards.

**Independent Test**: The Canvas client resolves secrets without hardcoded strings, failing gracefully with a clear exception if secrets are missing.

**Acceptance Scenarios**:

1. **Given** Secret Manager secret `canvas-api-token`, **When** the client initializes, **Then** it retrieves the token securely at runtime.

---

### User Story 3 - Normalized Data Schema Mapping (Priority: P2)

As a system developer, I want raw Canvas JSON API responses mapped into technology-agnostic Python data classes (`CanvasAssignment`, `CanvasCourse`) so that downstream business rules do not depend on raw JSON schema details.

**Why this priority**: Decouples API client payloads from core sentinel business logic.

**Independent Test**: Data models validate required fields and handle missing optional fields gracefully.

**Acceptance Scenarios**:

1. **Given** raw API JSON response, **When** passed through the Canvas parser, **Then** it outputs strongly-typed data structures with standardized UTC timestamp parsing.

---

### Edge Cases

- How does the system handle Canvas API rate limiting (HTTP 429)?
  - Implements exponential backoff retry logic for transient HTTP 429 / 5xx errors.
- What happens if an observee has no missing submissions?
  - Returns an empty list cleanly without throwing null pointer or parsing errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a Python Canvas ingestion client in `src/ingestion/canvas.py`.
- **FR-002**: System MUST retrieve Canvas access tokens securely from GCP Secret Manager secret `canvas-api-token` with local env fallback (`CANVAS_API_TOKEN`).
- **FR-003**: System MUST query missing submissions (`/api/v1/users/:observee_id/missing_submissions`) and course assignment lists.
- **FR-004**: System MUST parse and map API responses into Python data classes (`CanvasAssignment`, `CanvasCourse`).
- **FR-005**: System MUST implement exponential backoff for transient Canvas HTTP errors.

### Key Entities

- **CanvasAssignment**: Represets a Canvas assignment entity (`id`, `title`, `course_id`, `due_at`, `submission_types`, `points_possible`, `missing`).
- **CanvasCourse**: Represents a Canvas course enrollment (`id`, `name`, `course_code`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Canvas API response parsing completes in under 2 seconds for a student observee profile with up to 10 courses and 50 missing assignments.
- **SC-002**: Unit and integration test suite covers 100% of Canvas API parser mapping edge cases and error handlers.
