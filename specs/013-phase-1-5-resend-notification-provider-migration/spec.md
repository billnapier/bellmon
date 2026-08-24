# Feature Specification: Migration from SendGrid to Resend Email Notification Provider

**Feature Branch**: `013-phase-1-5-resend-notification-provider-migration`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Migrate email notification infrastructure from SendGrid API v3 to Resend API (`POST https://api.resend.com/emails`) across client implementation, router integration, test suite, and configuration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resend REST API Email Delivery Client (Priority: P1)

As a system engineer, I want a dedicated `ResendClient` that communicates with Resend's REST API (`https://api.resend.com/emails`) using standard Bearer token authorization (`RESEND_API_KEY`) so that email notification dispatching uses my existing Resend account.

**Why this priority**: Core integration point replacing the legacy SendGrid client.

**Independent Test**: Invoking `ResendClient.send_email()` with valid parameters makes an HTTP POST request to `https://api.resend.com/emails` with the `Authorization: Bearer <RESEND_API_KEY>` header and correct JSON payload (`from`, `to`, `subject`, `html`, `text`).

**Acceptance Scenarios**:

1. **Given** a configured `RESEND_API_KEY` and recipient email, **When** dispatch is triggered, **Then** `ResendClient` sends the payload to `https://api.resend.com/emails` and returns a successful `DispatchResult` containing the Resend email ID.
2. **Given** missing `RESEND_API_KEY` or `dry_run=True`, **When** dispatch is triggered, **Then** `ResendClient` logs the email content to stdout/logs and returns a simulated success `DispatchResult`.

---

### User Story 2 - Notification Router Migration & Fallback Handling (Priority: P1)

As the Bellmon notification orchestrator, I want `NotificationRouter` to utilize `ResendClient` by default so that all P0 academic alert emails are delivered seamlessly via Resend.

**Why this priority**: Ensures the high-level router seamlessly delegates dispatching to the new provider without breaking existing HTML rendering or alert batching logic.

**Independent Test**: Running `NotificationRouter.send_alerts()` triggers `ResendClient` to format and deliver aggregated P0 email packages.

**Acceptance Scenarios**:

1. **Given** pending P0 alerts for a student, **When** `router.send_alerts()` is called, **Then** it delegates to `ResendClient` using `RESEND_API_KEY` configuration.
2. **Given** an HTTP error from Resend (e.g., status 422 or 500), **When** dispatch fails, **Then** `ResendClient` captures the error message and returns `success=False` in `DispatchResult`.

---

### User Story 3 - Test Suite Update & Environment Standardization (Priority: P1)

As a developer, I want the unit test suite (`tests/test_notifications.py`) and module exports (`src/notifications/__init__.py`) to fully cover `ResendClient` so that code quality and CI pipeline validations pass with 100% coverage.

**Why this priority**: Prevents regressions and maintains code quality standards codified in the project constitution.

**Independent Test**: Running `pytest tests/test_notifications.py` succeeds with all tests passing, validating dry-run and mocked HTTP calls for Resend.

**Acceptance Scenarios**:

1. **Given** unit tests for notification delivery, **When** `pytest` executes, **Then** all tests pass validating `ResendClient` dry-run simulation and mocked HTTP REST API dispatch.

---

### Edge Cases

- What happens if `RESEND_API_KEY` is not defined in the environment?
  - `ResendClient` automatically falls back to dry-run simulation mode with a warning log, ensuring non-production environments operate without failing.
- What if the Resend API endpoint responds with non-2xx status codes (e.g. invalid domain verification or invalid API key)?
  - The client logs detailed API error messages and returns `DispatchResult(success=False, error_message=...)` to allow batch runner retry handling.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `ResendClient` in `src/notifications/resend.py`.
- **FR-002**: System MUST send HTTP POST requests to `https://api.resend.com/emails` with JSON body format: `{"from": ..., "to": [...], "subject": ..., "html": ..., "text": ...}`.
- **FR-003**: System MUST inspect `RESEND_API_KEY` environment variable as the default secret source.
- **FR-004**: System MUST support dry-run simulation mode when `RESEND_API_KEY` is absent or `dry_run=True`.
- **FR-005**: System MUST update `NotificationRouter` in `src/notifications/router.py` to instantiate and use `ResendClient`.
- **FR-006**: System MUST update module exports in `src/notifications/__init__.py` to expose `ResendClient`.
- **FR-007**: System MUST update `tests/test_notifications.py` to verify `ResendClient` behavior.

### Key Entities

- **ResendClient**: Client class managing HTTP connection to Resend API.
- **DispatchResult**: Structured response containing `success`, `message_id`, `recipient`, `timestamp`, and `error_message`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of email notification unit tests pass against `ResendClient` mock and dry-run instances.
- **SC-002**: Zero references to legacy `SendGridClient` or `SENDGRID_API_KEY` remain in active codebase logic.
