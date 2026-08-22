# Tasks: Phase 0.1 Infrastructure & Guardian CI/CD Foundation

**Input**: Design documents from `/specs/001-phase-0-1-infrastructure-poc/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial project layout and configuration files

- [x] T001 Create project directory structure (`src/`, `tests/`, `terraform/`, `.github/workflows/`)
- [x] T002 Create `pyproject.toml` with Python 3.11+ configuration and GCP dependencies (`google-cloud-firestore`, `google-cloud-secretmanager`, `pytest`)
- [x] T003 [P] Create `.gitignore` to exclude Terraform state files, Python `__pycache__`, and credentials

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Baseline Python package initialization and sanity test suite

- [x] T004 [P] Create base module `src/__init__.py` and placeholder batch entrypoint `src/main.py`
- [x] T005 [P] Create test package `tests/__init__.py` and baseline health test `tests/test_sanity.py`

---

## Phase 3: User Story 1 - Declarative Infrastructure Definition (Priority: P1) 🎯 MVP

**Goal**: Provision declarative GCP infrastructure (Secret Manager, Firestore, Service Accounts, Cloud Run Job skeleton) via Terraform in `terraform/`.

**Independent Test**: Running `terraform validate` and `terraform plan` produces a valid speculative execution plan with zero errors.

- [x] T006 [P] [US1] Create `terraform/main.tf` defining GCP provider configuration and GCS remote backend
- [x] T007 [P] [US1] Create `terraform/variables.tf` declaring input variables (`project_id`, `region`, `environment`)
- [x] T008 [P] [US1] Create `terraform/secrets.tf` defining Secret Manager secret containers (`canvas-api-token`, `powerschool-credentials`)
- [x] T009 [P] [US1] Create `terraform/firestore.tf` defining Cloud Firestore in Native Mode database instance
- [x] T010 [P] [US1] Create `terraform/iam.tf` defining Service Account and IAM role bindings (`roles/datastore.user`, `roles/secretmanager.secretAccessor`)
- [x] T011 [P] [US1] Create `terraform/cloud_run.tf` defining Cloud Run Job skeleton resource definition

---

## Phase 4: User Story 2 - Automated Guardian CI/CD Actuation (Priority: P1)

**Goal**: Configure GitHub Actions using Google's Guardian (`abcxyz/guardian`) workflow to execute speculative Terraform plans on PRs and automated applies on merge.

**Independent Test**: Opening a pull request triggers Guardian to comment formatted speculative Terraform diffs on PRs.

- [x] T012 [US2] Create `.github/workflows/guardian.yml` configuring `abcxyz/guardian` actions (`guardian plan` on PR, `guardian apply` on merge to `main`)

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation, formatting, and sanity verification

- [x] T013 [P] Format and validate Terraform files using `terraform fmt -check` and `terraform validate`
- [x] T014 Execute local pytest suite (`pytest`) to verify Python runtime environment sanity
- [x] T015 Verify quickstart instructions in `specs/001-phase-0-1-infrastructure-poc/quickstart.md`
