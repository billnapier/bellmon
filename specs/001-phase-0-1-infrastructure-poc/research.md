# Research & Architectural Trade-off Decisions: Micro-Spec 0.1

**Feature Branch**: `001-phase-0-1-infrastructure-poc`

---

## 1. CI/CD Actuation Engine: Google Guardian (`abcxyz/guardian@v3.2.5`)

* **Decision**: Adopt Google's **Guardian** (`github.com/abcxyz/guardian@v3.2.5`) GitHub Actions workflow.
* **Rationale**: Guardian provides automated, secure Terraform plan and apply execution natively integrated into GitHub PR workflows. It formats speculative plan diffs directly in PR comments and prevents unapproved infrastructure mutations.
* **Constitution v1.2.0 Compliance**: Authenticates using `google-github-actions/auth@v1` with GitHub Secrets (`${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}` and `${{ secrets.GCP_SERVICE_ACCOUNT }}`). Zero hardcoded fake placeholders.

---

## 2. Secrets Management Strategy

* **Decision**: GCP Secret Manager with secret container declarations in Terraform (`terraform/secrets.tf`).
* **Rationale**: Storing Canvas tokens and PowerSchool SSO credentials in GCP Secret Manager prevents plain-text secret exposure. Secret containers are defined declaratively in Terraform, while actual secret payloads are injected securely at runtime or via environment variables during local testing.

---

## 3. Database & State Store: Firestore Native Mode

* **Decision**: Provision Google Cloud Firestore in **Native Mode** (`(default)` database).
* **Rationale**: Firestore Native Mode provides serverless, auto-scaling document storage for session cookies (`psaid`), student grade snapshots, and missing assignment ledgers with zero database administration overhead.

---

## 4. Single Environment Deployment Strategy ("Test in Prod")

* **Decision**: Single GCP Production environment deployment model per Constitution Principle 1.
