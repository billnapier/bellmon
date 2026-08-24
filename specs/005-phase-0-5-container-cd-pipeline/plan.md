# Implementation Plan: Phase 0.5 Automated Container CI/CD Pipeline

**Branch**: `005-phase-0-5-container-cd-pipeline`  
**Spec**: [`specs/005-phase-0-5-container-cd-pipeline/spec.md`](file:///home/napier/a/bellmon/specs/005-phase-0-5-container-cd-pipeline/spec.md)  
**Status**: In Progress  

---

## Constitution Check

- [x] **Principle 1 (Test-in-Prod)**: Single production environment targeted by CI/CD.
- [x] **Principle 2 (Zero-Trust Secrets)**: Credentials injected via GitHub Secrets (`GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`).
- [x] **Principle 4 (Zero Fake Placeholders)**: Uses dynamic GitHub Secrets and workspace repository paths without hardcoded fake values.
- [x] **Principle 5 (PR-Only Enforcement)**: All workflow changes submitted via Pull Request.
- [x] **Principle 7 (Automated Container CI/CD)**: Fulfills mandatory rule requiring automated container build, push to Artifact Registry, and Cloud Run Job update on merge to `main`.

---

## Proposed Changes

### GitHub Actions Workflows

#### [NEW] `.github/workflows/cd-container.yml`

Create a dedicated workflow for continuous deployment of the containerized batch runner.

- **Triggers**: `push` to `main` with paths `src/**`, `Dockerfile`, `pyproject.toml`, `requirements.txt`, `.github/workflows/cd-container.yml`.
- **Jobs**:
  - `deploy-container`:
    - `actions/checkout@v3`
    - `google-github-actions/auth@v1` with Workload Identity Federation
    - `google-github-actions/setup-gcloud@v1`
    - Configure docker auth for `us-central1-docker.pkg.dev`
    - Build and push Docker image with tags `${{ github.sha }}` and `latest`
    - Execute `gcloud run jobs update bellmon-sentinel-job --image us-central1-docker.pkg.dev/bellmon/bellmon-repo/sentinel-batch:${{ github.sha }} --region us-central1`

---

## Verification Plan

### Automated Validation

1. Validate GitHub Actions syntax using local validation / manual review.
2. Trigger test commit or PR to verify workflow syntax and permissions.
3. Validate Cloud Run Job update commands using `gcloud run jobs describe bellmon-sentinel-job --region us-central1`.
