# Implementation Tasks: Migration from SendGrid to Resend Email Provider

## User Story 1 - Resend REST API Client Implementation

- [x] Task 1.1: Create `src/notifications/resend.py` implementing `ResendClient` class with HTTP REST dispatch to `https://api.resend.com/emails` and dry-run fallback when `RESEND_API_KEY` is missing or `dry_run=True`.
- [x] Task 1.2: Update `src/notifications/models.py` docstrings to reference Resend.
- [x] Task 1.3: Update `src/notifications/__init__.py` to export `ResendClient`.

## User Story 2 - Router & Integration Refactoring

- [x] Task 2.1: Refactor `src/notifications/router.py` to use `ResendClient` instead of `SendGridClient`.
- [x] Task 2.2: Remove deprecated `src/notifications/sendgrid.py` file.

## User Story 3 - Unit Testing & Verification

- [x] Task 3.1: Update `tests/test_notifications.py` to replace SendGrid client unit tests with `ResendClient` unit tests (testing dry-run simulation, successful REST API dispatch, and HTTP error handling).
- [x] Task 3.2: Run `pytest` across full test suite to ensure 100% test pass rate.
