# Implementation Plan: Migration from SendGrid to Resend Email Notification Provider

**Branch**: `013-phase-1-5-resend-notification-provider-migration` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/013-phase-1-5-resend-notification-provider-migration/spec.md`

## Summary

Migrate the email delivery infrastructure from SendGrid (`SendGridClient`, `SENDGRID_API_KEY`) to Resend (`ResendClient`, `RESEND_API_KEY`). Update `src/notifications/resend.py`, `src/notifications/router.py`, `src/notifications/models.py`, `src/notifications/__init__.py`, and `tests/test_notifications.py`.

## Technical Context

- **Source API**: Resend REST API (`POST https://api.resend.com/emails`)
- **Headers**: `Authorization: Bearer <RESEND_API_KEY>`, `Content-Type: application/json`
- **Payload Schema**:
  ```json
  {
    "from": "Bellmon Academic Sentinel <alerts@bellmon.dev>",
    "to": ["parent@example.com"],
    "subject": "Subject Line",
    "html": "<html>...</html>",
    "text": "Plaintext..."
  }
  ```
- **Fallback**: Automatic dry-run simulation when `RESEND_API_KEY` is not provided or `dry_run=True`.

## System Architecture & Component Touches

```
src/notifications/
├── resend.py        # NEW: Resend REST API client implementation
├── sendgrid.py      # REMOVED / REPLACED by resend.py
├── router.py        # UPDATED: Router instantiates and uses ResendClient
├── models.py        # UPDATED: Updated docstrings and models for Resend
└── __init__.py      # UPDATED: Export ResendClient instead of SendGridClient

tests/
└── test_notifications.py  # UPDATED: Tests for ResendClient live & dry-run dispatch
```

## Constitution Check

- [x] **Principle 1 (Asymmetric Authority Model)**: Notification router respects asymmetric authority rules.
- [x] **Principle 2 (Zero-Trust Secrets Management)**: `RESEND_API_KEY` fetched dynamically from environment variables, fallback to dry-run mode if unconfigured.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: All changes implemented on branch `013-phase-1-5-resend-notification-provider-migration` and verified via unit tests.
