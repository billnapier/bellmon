# Quickstart Guide: Academic & Workload Sentinel

**Feature**: `002-academic-sentinel`  
**Date**: 2026-08-20  

## Local Setup & Development

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Environment Configuration
Create a `.env` file in project root:

```bash
CANVAS_API_TOKEN="your_canvas_token"
CANVAS_BASE_URL="https://canvas.bellarmine.org"
POWERSCHOOL_BASE_URL="https://powerschool.bellarmine.org"
POWERSCHOOL_USERNAME="your_username"
POWERSCHOOL_PASSWORD="your_password"
PUSHOVER_USER_KEY="your_pushover_user"
PUSHOVER_APP_TOKEN="your_pushover_app_token"
SMTP_SERVER="smtp.sendgrid.net"
SMTP_PORT="587"
SMTP_USER="apikey"
SMTP_PASSWORD="your_sendgrid_key"
```

### 3. Execution Commands

#### Run Ingestion & Rule Evaluator (CLI mode)
```bash
python -m src.cli.sync --student-id student_123
```

#### Run Test Suite
```bash
pytest tests/unit/ tests/integration/
```

### 4. Infrastructure & CI/CD Deployment (Terraform + Guardian)

#### Local Terraform Plan Verification
```bash
cd terraform/
terraform init
terraform plan
```

#### Automated CI/CD Pipeline (GitHub Actions + Guardian)
- **Pull Request Trigger**: `.github/workflows/guardian-plan.yml` runs Guardian (`abcxyz/guardian`) to plan changes and post a structured plan comment on PRs.
- **Merge Trigger**: `.github/workflows/guardian-apply.yml` executes policy-enforced `terraform apply` to deploy Cloud Run container updates and Cloud Scheduler triggers.

