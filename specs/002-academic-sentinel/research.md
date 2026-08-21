# Research & Technical Decisions: Academic & Workload Sentinel

**Feature**: `002-academic-sentinel`  
**Date**: 2026-08-20  

## Research Topics & Decisions

### 1. Ingestion & API Integration Strategy
- **Decision**: Python 3.11 asynchronous HTTP client (`httpx` / `aiohttp` or `requests` with retry backoff) executing on Google Cloud Run via Cloud Scheduler cron (5:00 PM weekdays, 6:00 PM Sunday).
- **Rationale**: Serverless deployment minimizes operational overhead and supports zero-touch background execution.
- **Alternatives Considered**: Dedicated VM cron (rejected due to maintenance overhead and cost).

### 2. State Storage & Idempotency Store
- **Decision**: Google Cloud Firestore (or SQLite for local CLI runs).
- **Rationale**: Firestore provides native JSON document storage, serverless scaling, atomic updates for state diffing, and fast key-value lookups for alert ledger entries.
- **Alternatives Considered**: PostgreSQL/Cloud SQL (rejected as unnecessary relational complexity for document state cache).

### 3. Missing Work & Grace Period Evaluation Engine
- **Decision**: 36-hour grace period calculated using ISO-8601 UTC timestamps stored in tracked assignment documents. State machine transition: `NEW` $\to$ `GRACE_PERIOD` $\to$ `ALERT_DISPATCHED` or `RESOLVED`/`SUPPRESSED`.
- **Rationale**: Clear state transitions prevent duplicate notifications and accurately preserve student autonomy buffer.

### 4. Push & Email Delivery Channels
- **Decision**: Direct HTTP webhooks for Pushover / NTFY (P0 Push) and SendGrid / SMTP (P1 Sunday Email Digest).
- **Rationale**: High reliability delivery with minimal latency for P0 mobile alerts and rich HTML templating (Jinja2) for Sunday digests.

### 5. Infrastructure as Code (Terraform)
- **Decision**: Terraform 1.5+ declaring Google Cloud Run, Cloud Scheduler, Firestore Database, and IAM Service Account bindings in `terraform/`.
- **Rationale**: Declarative, reproducible infrastructure provisioning adhering to Principle 6 of the Project Constitution.
- **Alternatives Considered**: Manual GCP Console configuration (rejected per Principle 6 rule).

### 6. Automated CI/CD Deployment (GitHub Actions + Guardian)
- **Decision**: GitHub Actions workflows integrated with Guardian (`https://github.com/abcxyz/guardian`) for pull request plan comments and automated apply on merge.
- **Rationale**: Guardian provides secure, policy-enforced Terraform execution with automated plan review, secret protection, and audit logging.
- **Alternatives Considered**: Manual `terraform apply` from local developer machines (rejected due to security and consistency risks).

