<!--
Sync Impact Report:
- Version change: v1.2.0 -> v1.2.1
- Modified Sections: Principle 4 (Zero Fake Placeholders & Zero-Edit Executable Scripts)
- Added Guidance: Setup scripts in quickstart.md and chat action items MUST be zero-edit copy-paste executable using dynamic shell variables.
- Status: ✅ Constitution ratified v1.2.1
-->

# Project Constitution: Bellmon (Bellarmine Monitor)

**Version**: 1.2.1  
**Ratified**: 2026-08-21  
**Last Amended**: 2026-08-21  

---

## Core Principles

### Principle 1: Test-in-Prod Single Environment Model
The project standardizes on a single production deployment environment ("Test in Prod"). Staging environment overhead is prohibited to eliminate maintenance bloat and cloud cost multiplier. Quality is enforced via isolated unit tests (`pytest`), local Terraform validation (`terraform validate`), and atomic batch execution.

### Principle 2: Zero-Trust Secrets & Credential Isolation
No plain-text tokens, passwords, or SAML credentials shall ever be committed to source code or git history. All sensitive values MUST be stored in GCP Secret Manager (`canvas-api-token`, `powerschool-credentials`) or injected securely at runtime via environment variables.

### Principle 3: Asymmetric System Authority
PowerSchool SIS is the authoritative system of record for official course grades, period-level attendance, and formal transcripts. Canvas LMS is an auxiliary system of record for digital assignment submissions and due dates. The engine MUST evaluate missing work independently per system without enforcing title-matching across platforms.

### Principle 4: Zero Fake Placeholders & Zero-Edit Executable Scripts *(Refined)*
* **No Hardcoded Placeholders**: Agents and developers MUST NEVER output hardcoded fake placeholders (e.g., `123456789`, `my-project-id`, `dummy-token`) in source code, Terraform configurations, or CI/CD workflow files.
* **GitHub Secrets Enforcement**: All infrastructure identifiers, project numbers, service accounts, and API tokens in CI/CD workflows MUST reference GitHub Secrets (e.g., `${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}`).
* **Zero-Edit Human Action Scripts**: Setup scripts in `quickstart.md` and chat action items MUST be 100% copy-paste executable. They MUST dynamically derive project numbers and environment variables using subshells (e.g., `export GCP_PROJECT_NUMBER=$(gcloud projects describe ...)`), requiring ZERO manual string editing or string hunting from the developer.

---

## Governance & Compliance

* **Specification Precedence**: All implementation code MUST trace directly to an approved feature specification (`spec.md`).
* **Amendment Policy**: Changes to this constitution require a semantic version bump (MAJOR for principle removals, MINOR for new principles, PATCH for wording refinements).
