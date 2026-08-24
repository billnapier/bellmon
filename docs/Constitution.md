<!--
Sync Impact Report:
- Version change: v1.6.0 -> v1.7.0
- Added Sections: Principle 7 (Automated Container CI/CD & Hands-Free Deployment)
- Modified Guidance: Mandates automated container image building, tagging with commit SHA and latest, pushing to GCP Artifact Registry, and updating Cloud Run resources upon Pull Request merge to main.
- Status: ✅ Constitution ratified v1.7.0
-->

# Project Constitution: Bellmon (Bellarmine Monitor)

**Version**: 1.7.0  
**Ratified**: 2026-08-21  
**Last Amended**: 2026-08-23  

---

## Core Principles

### Principle 1: Test-in-Prod Single Environment Model
The project standardizes on a single production deployment environment ("Test in Prod"). Staging environment overhead is prohibited to eliminate maintenance bloat and cloud cost multiplier. Quality is enforced via isolated unit tests (`pytest`), local Terraform validation (`terraform validate`), and atomic batch execution.

### Principle 2: Zero-Trust Secrets & Credential Isolation
No plain-text tokens, passwords, or SAML credentials shall ever be committed to source code or git history. All sensitive values MUST be stored in GCP Secret Manager (`canvas-api-token`, `powerschool-credentials`) or injected securely at runtime via environment variables.

### Principle 3: Asymmetric System Authority
PowerSchool SIS is the authoritative system of record for official course grades, period-level attendance, and formal transcripts. Canvas LMS is an auxiliary system of record for digital assignment submissions and due dates. The engine MUST evaluate missing work independently per system without enforcing title-matching across platforms.

### Principle 4: Zero Fake Placeholders & Dynamic Environment Querying
* **No Hardcoded Placeholders or Invented Names**: Agents MUST NEVER invent, guess, or hardcode fake placeholders or project names (e.g., `123456789`, `bellmon-prod`, `my-project-id`, `dummy-token`) in source code, Terraform configurations, or CI/CD workflow files.
* **No Default Project Variables**: Terraform `variables.tf` files MUST NOT specify hardcoded `default` values for GCP Project IDs or account names unless explicitly declared in the spec.
* **GitHub Secrets Enforcement**: All infrastructure identifiers, project numbers, service accounts, and API tokens in CI/CD workflows MUST reference GitHub Secrets (e.g., `${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}`).
* **Dynamic Environment Querying**: Setup scripts in `quickstart.md` and chat action items MUST be 100% copy-paste executable. They MUST dynamically derive project names and IDs from the developer's live CLI environment (e.g., `export GCP_PROJECT_ID=$(gcloud config get-value project)` and `export GCP_PROJECT_NUMBER=$(gcloud projects describe ...)`), requiring ZERO manual string editing or string hunting from the developer.

### Principle 5: PR-Only Enforcement & Mandatory CI Testing
* **No Direct Pushes to Main**: AI agents and human developers MUST NEVER push commits directly to `main` under any circumstances (including bug fixes, documentation updates, or workflow adjustments).
* **Mandatory PR Lifecycle**: All code, configuration, workflow, and infrastructure modifications MUST be committed to a dedicated feature/fix branch and submitted via a GitHub Pull Request (`gh pr create`).
* **Mandatory CI Unit Test Execution**: CI workflows MUST automatically run the complete Python test suite (`pytest`) on every Pull Request targeting `main` to guarantee zero regressions prior to merge approval.
* **Guardian PR-Bound Lifecycle**: Guardian CLI relies on GitHub Pull Request metadata to bind and retrieve Terraform plan files stored in Google Cloud Storage (`-storage=gcs://bellmon-tf-state`). Submitting a Pull Request and merging it is the ONLY valid mechanism for executing infrastructure changes in CI/CD.

### Principle 6: Open-Source First & Justified Custom Auth
* **Prefer Standard Open-Source Libraries**: Developers and AI agents MUST prioritize using established open-source software (OSS) libraries, official SDKs, and PyPI packages (e.g., `requests`, `pydantic`, `google-cloud-*`, `beautifulsoup4`) for data models, API integrations, and system parsing.
* **Justified Custom Auth Models**: Custom authentication drivers (e.g., Playwright SAML SSO scrapers) are permitted ONLY when official REST/OAuth API access is unavailable or locked down by institution policies. Custom auth models MUST explicitly document why standard OSS client libraries cannot be used.

### Principle 7: Automated Container CI/CD & Hands-Free Deployment
* **Automated Container CD on Merge**: Merging a Pull Request to `main` MUST automatically trigger container image builds (`docker build`), tag images with commit SHA (`${{ github.sha }}`) and `latest`, push to GCP Artifact Registry, and update Cloud Run jobs/services (`gcloud run jobs update`) without manual CLI interventions.
* **Zero Manual Production Builds**: Developer machines MUST NOT be used to manually build or push production container images. All production container artifacts MUST be built reproducibly by GitHub Actions CI/CD workflows.
* **Traceable Deployment Artifacts**: Every deployed container image in GCP Artifact Registry and Cloud Run MUST be traceable directly to an explicit commit SHA in `main`.

---

## Governance & Compliance

* **Specification Precedence**: All implementation code MUST trace directly to an approved feature specification (`spec.md`).
* **Amendment Policy**: Changes to this constitution require a semantic version bump (MAJOR for principle removals, MINOR for new principles, PATCH for wording refinements).
