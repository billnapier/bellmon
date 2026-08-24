# Feature Specification: Phase 0.5 Automated Container CI/CD Pipeline & Hands-Free Cloud Run Deployment

**Feature Branch**: `005-phase-0-5-container-cd-pipeline`  
**Created**: 2026-08-23  
**Status**: Draft  
**Input**: Hands-free CD pipeline for building, tagging, pushing Docker images to GCP Artifact Registry and updating Cloud Run Job on PR merge to main

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Container Image Build & Push on Merge (Priority: P1)

As a maintainer, I want GitHub Actions to automatically build the production Docker image and push it to GCP Artifact Registry whenever code changes are merged into `main`, so that manual local builds are eliminated and container builds are 100% reproducible.

**Why this priority**: Enforces Principle 7 of the Project Constitution (Automated Container CI/CD & Hands-Free Deployment).

**Independent Test**: Merging a PR to `main` with application changes (`src/**`, `Dockerfile`, `pyproject.toml`) triggers the container build workflow, which tags the image with both `${{ github.sha }}` and `latest` and pushes them to `us-central1-docker.pkg.dev/bellmon/bellmon-repo/sentinel-batch`.

**Acceptance Scenarios**:

1. **Given** code pushed to `main`, **When** the `cd-container.yml` workflow runs, **Then** it authenticates to GCP via Workload Identity Provider and logs into Artifact Registry.
2. **Given** successful authentication, **When** `docker build` runs in CI, **Then** the image is built using the workspace `Dockerfile` and tagged with `${{ github.sha }}` and `latest`.
3. **Given** image build completion, **When** `docker push` runs, **Then** both tags are stored in GCP Artifact Registry.

---

### User Story 2 - Automated Cloud Run Job Image Update (Priority: P1)

As a DevOps engineer, I want the CD pipeline to update the Cloud Run Job `bellmon-sentinel-job` with the newly pushed container image tag automatically, so that subsequent scheduled or manual job executions run the latest merged code immediately.

**Why this priority**: Completes hands-free deployment without requiring developers to run `gcloud run jobs update` from local terminals.

**Independent Test**: The CD workflow executes `gcloud run jobs update bellmon-sentinel-job --image us-central1-docker.pkg.dev/bellmon/bellmon-repo/sentinel-batch:${{ github.sha }} --region us-central1` and succeeds.

**Acceptance Scenarios**:

1. **Given** a pushed container image tag, **When** `gcloud run jobs update` executes in CI, **Then** the Cloud Run Job image reference is updated to match the commit SHA.
2. **Given** job configuration update, **When** `gcloud run jobs describe bellmon-sentinel-job` is queried, **Then** the active image points to the newly deployed container tag.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a GitHub Actions workflow `.github/workflows/cd-container.yml`.
- **FR-002**: Workflow MUST trigger on `push` to `main` for changes in `src/**`, `Dockerfile`, `pyproject.toml`, `requirements.txt`, or `.github/workflows/cd-container.yml`.
- **FR-003**: Workflow MUST authenticate to GCP using `google-github-actions/auth` and Workload Identity secrets (`GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`).
- **FR-004**: Workflow MUST log into GCP Artifact Registry using `google-github-actions/setup-gcloud` or `docker/login-action`.
- **FR-005**: Workflow MUST build the container image and tag it with both the commit SHA (`${{ github.sha }}`) and `latest`.
- **FR-006**: Workflow MUST push both tags to `us-central1-docker.pkg.dev/bellmon/bellmon-repo/sentinel-batch`.
- **FR-007**: Workflow MUST update `bellmon-sentinel-job` Cloud Run Job to use the newly pushed commit SHA image tag in region `us-central1`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CD workflow completes container build, push, and Cloud Run Job update in under 3 minutes on merge to `main`.
- **SC-002**: 100% of container images deployed to Cloud Run match the exact Git commit SHA from `main`.
- **SC-003**: Zero manual developer intervention required for production deployments.
