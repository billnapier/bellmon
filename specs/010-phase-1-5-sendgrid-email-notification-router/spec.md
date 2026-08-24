# Feature Specification: Phase 1.5 SendGrid Responsive HTML Email Notification Router & Integration

**Feature Branch**: `010-phase-1-5-sendgrid-email-notification-router`  
**Created**: 2026-08-24  
**Status**: Draft  
**Input**: Phase 1.5 Responsive HTML email templates, SendGrid Web API router, notification dispatching, and end-to-end main.py batch integration

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Responsive HTML P0 Alert Email Templates (Priority: P1)

As a parent, I want visually clear, responsive HTML email notifications formatted for mobile and desktop screens so that P0 alerts (Confirmed Missing Work, Grade Velocity Drop, Attendance Anomalies) are easy to read and act upon immediately.

**Why this priority**: High-fidelity visual communication ensures urgent alerts stand out and convey key academic information clearly.

**Independent Test**: Rendering the email templates with sample alert payloads produces valid responsive HTML containing clear section headers, course names, and action items.

**Acceptance Scenarios**:

1. **Given** pending P0 alert payloads (Missing Work, Grade Drop, Attendance Anomaly), **When** email template renderer is called, **Then** it compiles responsive HTML email bodies with distinct visual sections for each alert category.
2. **Given** mobile email clients, **When** email is opened, **Then** single-column layout and typography adjust cleanly for small screens.

---

### User Story 2 - SendGrid Web API Router & Dry-Run Fallback (Priority: P1)

As a system orchestrator, I want a notification router that sends compiled HTML emails via the SendGrid Web API (or logs them in dry-run mode when unconfigured) so that alert delivery is reliable and testable without sending actual emails during development.

**Why this priority**: Reliable email delivery mechanism with built-in test/dry-run capability for developer confidence.

**Independent Test**: Invoking the notification router in dry-run mode logs the full compiled HTML payload to stdout and returns a success status.

**Acceptance Scenarios**:

1. **Given** configured SendGrid API key and recipient email, **When** dispatch is triggered, **Then** router sends HTML email via SendGrid Web API v3 and returns a successful message ID.
2. **Given** missing SendGrid API key or dry-run flag, **When** dispatch is triggered, **Then** router logs the email body to console/logs and marks delivery as simulated success.

---

### User Story 3 - End-to-End Batch Orchestration Integration (Priority: P1)

As the Bellmon batch runtime, I want `src/main.py` to seamlessly execute the complete ingestion-to-notification pipeline (Harvest -> Load Firestore -> Run Alert Engines -> Send Email -> Save Firestore State) so that daily 5:00 PM executions operate autonomously.

**Why this priority**: Integrates all Phase 1 components into a single executable automated pipeline.

**Independent Test**: Running `python -m src.main` executes harvesting, state management, alert evaluation, notification dispatching, and Firestore persistence sequentially with exit code 0.

**Acceptance Scenarios**:

1. **Given** complete Phase 1 setup, **When** `src.main` executes, **Then** it runs Canvas & PowerSchool harvesting, evaluates grace period, grade velocity, and attendance engines, dispatches aggregated P0 email if pending alerts exist, and updates Firestore state.
2. **Given** successful email dispatch, **When** job completes, **Then** Firestore tracked assignments and attendance events are updated with `alert_dispatched: true` / `notified: true`.

---

### Edge Cases

- What happens if SendGrid API returns a transient HTTP error (e.g. 503 or 429)?
  - The router logs the failure; Firestore state is NOT updated (`alert_dispatched` remains `false`), allowing the next batch execution to retry delivery.
- How does the router handle runs where zero P0 alerts are generated?
  - Skips email dispatch entirely, logging "Zero P0 alerts pending; no email sent."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement `NotificationRouter` in `src/notifications/router.py` and `SendGridClient` in `src/notifications/sendgrid.py`.
- **FR-002**: System MUST build responsive HTML templates in `src/notifications/templates/` for P0 Missing Work, Grade Velocity Drop, and Attendance Anomaly alerts.
- **FR-003**: System MUST aggregate multiple pending P0 alerts for a single student into a single combined email dispatch per daily batch run.
- **FR-004**: System MUST support dry-run / local logging mode when `SENDGRID_API_KEY` is not present or when `DRY_RUN=true`.
- **FR-005**: System MUST update Firestore flags (`alert_dispatched: true`, `notified: true`) only after successful email transmission.
- **FR-006**: System MUST wire the complete pipeline into `src/main.py`: Ingestion -> Firestore Load -> Alert Engine Evaluation -> Email Notification Router -> Firestore Persist.

### Key Entities

- **EmailPayload**: Structure containing `recipient`, `subject`, `html_body`, `text_fallback`, and `alerts_included`.
- **DispatchResult**: Result object with `success`, `message_id`, `recipient`, `timestamp`, and `error_message`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Compiled HTML email templates pass responsive email rendering checks across desktop and mobile screen widths.
- **SC-002**: Combined email notifications prevent email flooding by sending at most 1 email per student per daily batch execution.
- **SC-003**: End-to-end `python -m src.main` batch execution completes cold start to finish with zero unhandled exceptions.
