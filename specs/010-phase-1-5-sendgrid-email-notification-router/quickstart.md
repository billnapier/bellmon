# Quickstart: Phase 1.5 SendGrid Responsive Email Router

## Running Unit Tests

Run the test suite covering email rendering, SendGrid REST API dispatch (and dry-run simulation), and main batch orchestration:

```bash
pytest tests/test_notifications.py tests/test_main.py -v
```

## Local Execution in Dry-Run Mode

Run the complete batch pipeline locally without sending actual emails:

```bash
DRY_RUN=true python -m src.main
```

## Local Execution with SendGrid API

To test live dispatch with a SendGrid API key:

```bash
export SENDGRID_API_KEY="SG.your_api_key_here"
export ALERT_RECIPIENT_EMAIL="parent@example.com"
python -m src.main
```
