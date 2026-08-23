# Feature Specification: Phase 0.1 Infrastructure & Guardian CI/CD Foundation

**Feature Branch**: `001-phase-0-1-infrastructure-poc`  
**Created**: 2026-08-21  
**Status**: Draft  
**Input**: Phase 0.1 Infrastructure setup with Terraform, GCP Secret Manager, Firestore, and Guardian CI/CD

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Declarative Infrastructure Definition (Priority: P1)

As a cloud system developer, I want all foundational Google Cloud Platform resources (Cloud Run Job skeleton, Cloud Firestore database instance, Secret Manager secret containers, Service Account, and IAM permissions) to be defined declaratively in Terraform code so that infrastructure changes are reproducible, version-controlled, and audit-ready.

**Why this priority**: Core infrastructure must exist before application code can store secrets, read session data, or run on Cloud Run.

**Independent Test**: Running speculative plan against GCP produces a clean terraform execution plan detailing resource creation without syntax or HCL errors.

**Acceptance Scenarios**:

1. **Given** clean terraform definitions in `terraform/`, **When** `terraform plan` is executed, **Then** it generates a valid speculative execution plan containing Cloud Run Job, Secret Manager resources (`canvas-api-token`, `powerschool-credentials`), Firestore DB instance, and IAM bindings.
2. **Given** terraform plan output, **When** applied, **Then** all GCP resources are provisioned with proper zero-trust service account bindings.

---

### User Story 2 - Automated Guardian CI/CD Actuation (Priority: P1)

As a repository maintainer, I want pull requests and main branch merges to trigger Google's Guardian GitHub Action workflow (`abcxyz/guardian`) so that speculative infrastructure plans are commented on PRs automatically and applied upon merge without manual CLI intervention.

**Why this priority**: Automated infrastructure CI/CD prevents configuration drift and enforces a single "Test in Prod" pipeline.

**Independent Test**: Creating a Pull Request with Terraform modifications triggers Guardian to output formatted speculative diffs in PR comments.

**Acceptance Scenarios**:

1. **Given** a pull request containing HCL changes in `terraform/`, **When** the PR is opened or updated, **Then** the Guardian GitHub Actions workflow runs `guardian plan` and posts a comment with the execution plan summary.
2. **Given** an approved pull request merged into `main`, **When** merge completes, **Then** the Guardian GitHub Actions workflow executes `guardian apply` to update GCP resources directly.

---

### User Story 3 - Base Project Runtime Structure (Priority: P2)

As a developer, I want a standardized Python 3.11 project layout (`pyproject.toml`, `src/`) so that dependencies, linting, and entrypoints are properly configured for subsequent ingestion modules.

**Why this priority**: Establishes standard project conventions before building Canvas and PowerSchool scraper modules.

**Independent Test**: Running test suite runner in `src/` executes baseline health check successfully.

**Acceptance Scenarios**:

1. **Given** the repository root, **When** inspecting project structure, **Then** `pyproject.toml` or `requirements.txt` defines core dependencies (Google Cloud SDKs, pytest) and `src/` contains package initialization.

---

### Edge Cases

- How does the system handle pre-existing GCP resources during initial `guardian apply`?
  - Terraform state is managed in a remote GCP Cloud Storage bucket backend to prevent collision.
- What happens if Secret Manager secrets are declared without secret values?
  - Secret containers are provisioned by Terraform; secret payload values are injected securely out-of-band or via workflow secrets.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define declarative Terraform configurations in `terraform/` for GCP Secret Manager secret containers (`canvas-api-token`, `powerschool-credentials`).
- **FR-002**: System MUST define Cloud Firestore in Native Mode for state and session storage.
- **FR-003**: System MUST define a GCP Service Account with minimal required IAM permissions for Cloud Run job execution and Firestore read/write access.
- **FR-004**: System MUST configure GitHub Actions workflow `.github/workflows/guardian.yml` using `abcxyz/guardian` for automated speculative plans on PRs and automated applies on `main` merge.
- **FR-005**: System MUST structure the Python runtime environment (`pyproject.toml`) supporting Python 3.11+.

### Key Entities

- **Terraform State**: Remote state object storing current state of GCP provisioned infrastructure.
- **Secret Container**: GCP Secret Manager holder for Canvas and PowerSchool authentication credentials.
- **Sentinel Service Account**: GCP IAM identity bound to Cloud Run execution runtime.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `guardian plan` workflow completes execution on pull requests in under 3 minutes.
- **SC-002**: 100% of required infrastructure components (Secret Manager, Firestore, IAM, Cloud Run Job skeleton) are provisioned via Terraform without manual GCP Console setup.
- **SC-003**: Zero plain-text credentials or API tokens exist in code repositories or commit histories.
