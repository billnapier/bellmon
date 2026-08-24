# Quickstart: Resend Email Provider Migration

## Running Unit Tests

Run the test suite covering email rendering, Resend REST API dispatch (and dry-run simulation), and main batch orchestration:

```bash
pytest tests/test_notifications.py -v
```

## Dry-Run Mode (Default)

When `RESEND_API_KEY` is not set or `DRY_RUN=true`, emails are simulated and logged to stdout:

```bash
python -m src.main
```

## Local Execution with Resend API Key

To test live email dispatch using your Resend account API key:

```bash
export RESEND_API_KEY="re_123456789"
python -m src.main
```
