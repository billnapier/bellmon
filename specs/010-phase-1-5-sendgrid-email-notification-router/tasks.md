# Implementation Tasks: Phase 1.5 SendGrid Responsive Email Router & Main Batch Integration

## User Story 1 - Responsive HTML P0 Alert Email Templates

- [x] Task 1.1: Define notification data models in `src/notifications/models.py` (`EmailPayload`, `DispatchResult`).
- [x] Task 1.2: Implement responsive HTML template renderer in `src/notifications/renderer.py` supporting single-column layout, color-coded alert badges (Missing Work, Grade Drop, Attendance Anomaly), and plaintext fallback.
- [x] Task 1.3: Add unit tests for email rendering in `tests/test_notifications.py`.

## User Story 2 - SendGrid Web API Router & Dry-Run Fallback

- [x] Task 2.1: Implement `SendGridClient` in `src/notifications/sendgrid.py` with HTTP REST dispatch to `https://api.sendgrid.com/v3/mail/send` and automatic dry-run simulation when `SENDGRID_API_KEY` is missing or `DRY_RUN=true`.
- [x] Task 2.2: Implement `NotificationRouter` in `src/notifications/router.py` to aggregate pending alerts, compile emails, and manage dispatch status.
- [x] Task 2.3: Add unit tests for `SendGridClient` and `NotificationRouter` in `tests/test_notifications.py`.

## User Story 3 - End-to-End Batch Orchestration Integration

- [x] Task 3.1: Wire complete ingestion-to-notification pipeline in `src/main.py`: Canvas & PowerSchool Harvest -> Firestore Load -> Grace Period Engine -> Grade Velocity Engine -> Attendance Sentinel -> Notification Router -> Firestore State Persist (`alert_dispatched=True`).
- [x] Task 3.2: Implement end-to-end integration unit tests in `tests/test_main.py`.
- [x] Task 3.3: Verify test suite execution (`pytest`) and update `specs/STATUS.md`.
