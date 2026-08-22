# Research & Architectural Trade-off Decisions: Micro-Spec 0.1

**Feature Branch**: `001-phase-0-1-infrastructure-poc`

---

## 1. CI/CD Actuation Engine: Google Guardian (`abcxyz/guardian`)

* **Decision**: Adopt Google's **Guardian** (`github.com/abcxyz/guardian`) GitHub Actions workflow.
* **Rationale**: Guardian provides automated, secure Terraform plan and apply execution natively integrated into GitHub PR workflows. It formats speculative plan diffs directly in PR comments and prevents unapproved infrastructure mutations.
* **Alternatives Considered**:
  * *Manual CLI `terraform apply`*: Rejected due to high risk of state drift and lack of auditability.
  * *Atlantis*: Rejected due to stateful server hosting requirements (Guardian is 100% serverless GitHub Action).

---

## 2. Secrets Management Strategy

* **Decision**: GCP Secret Manager with secret container declarations in Terraform (`terraform/secrets.tf`).
* **Rationale**: Storing Canvas tokens and PowerSchool SSO credentials in GCP Secret Manager prevents plain-text secret exposure. Secret containers are defined declaratively in Terraform, while actual secret payloads are injected securely at runtime or via environment variables during local testing.
* **Alternatives Considered**:
  * *Hardcoded values / `.env` files in git*: Strictly prohibited due to security policy.
  * *Vault*: Overkill for single-cloud GCP footprint.

---

## 3. Database & State Store: Firestore Native Mode

* **Decision**: Provision Google Cloud Firestore in **Native Mode** (`(default)` database).
* **Rationale**: Firestore Native Mode provides serverless, auto-scaling document storage for session cookies (`psaid`), student grade snapshots, and missing assignment ledgers with zero database administration overhead.
* **Alternatives Considered**:
  * *Cloud SQL (PostgreSQL)*: Rejected due to baseline compute costs ($30+/mo) for an idle DB.
  * *Datastore Mode*: Native Mode offers richer client libraries and real-time document listener capabilities.

---

## 4. Single Environment Deployment Strategy ("Test in Prod")

* **Decision**: Single GCP Production environment deployment model.
* **Rationale**: For an observer monitoring sentinel, maintaining duplicate staging environments introduces sync overhead and unnecessary cloud costs. Quality is enforced via local unit tests, speculative `guardian plan` checks, and atomic batch executions.
