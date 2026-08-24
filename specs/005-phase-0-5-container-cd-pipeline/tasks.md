# Tasks: Phase 0.5 Automated Container CI/CD Pipeline

**Branch**: `005-phase-0-5-container-cd-pipeline`  
**Spec**: [`specs/005-phase-0-5-container-cd-pipeline/spec.md`](file:///home/napier/a/bellmon/specs/005-phase-0-5-container-cd-pipeline/spec.md)  
**Plan**: [`specs/005-phase-0-5-container-cd-pipeline/plan.md`](file:///home/napier/a/bellmon/specs/005-phase-0-5-container-cd-pipeline/plan.md)  

---

## Task List

- [x] **Task 1: Create Container CD GitHub Workflow** `[P1]`
  - Create `.github/workflows/cd-container.yml`.
  - Configure GCP Workload Identity authentication.
  - Implement Docker build, tag (`${{ github.sha }}` & `latest`), and push steps to Artifact Registry (`us-central1-docker.pkg.dev/bellmon/bellmon-repo/sentinel-batch`).
  - Add Cloud Run Job update step (`gcloud run jobs update bellmon-sentinel-job`).

- [ ] **Task 2: Commit, Push, and Open GitHub Pull Request** `[P1]`
  - Commit all feature spec and workflow changes to `005-phase-0-5-container-cd-pipeline`.
  - Push branch to GitHub.
  - Submit Pull Request using `gh pr create`.
