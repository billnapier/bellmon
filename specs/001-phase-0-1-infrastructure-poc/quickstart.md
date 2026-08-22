# Quickstart Guide: Micro-Spec 0.1 Infrastructure & Guardian CI/CD Foundation

**Feature Branch**: `001-phase-0-1-infrastructure-poc`

---

## 1. Required GitHub Repository Secrets

Per Constitution Principle 4, configure the following secrets in GitHub (**Settings > Secrets and variables > Actions**):

| Secret Name | Description | Example / Value Format |
| :--- | :--- | :--- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Full resource name of Workload Identity Provider | `projects/123456789/locations/global/workloadIdentityPools/pool/providers/provider` |
| `GCP_SERVICE_ACCOUNT` | Service Account email for Guardian | `bellmon-sentinel-runner@bellmon-prod.iam.gserviceaccount.com` |

---

## 2. Local Workstation Setup

1. **Install Python Dependencies**:
   ```bash
   pip install -e .
   ```

2. **Authenticate with GCP**:
   ```bash
   gcloud auth application-default login
   ```

---

## 3. Terraform Infrastructure Validation

Validate HCL syntax and formatting locally before pushing:

```bash
cd terraform
terraform init -backend=false
terraform fmt -check
terraform validate
```

---

## 4. Guardian CI/CD Verification

1. **Commit and Push Changes**:
   ```bash
   git add .
   git commit -m "feat(infra): apply constitution v1.2.0 secret contract"
   git push origin 001-phase-0-1-infrastructure-poc
   ```

2. **Open Pull Request**:
   * Creating a PR triggers `.github/workflows/guardian.yml`.
   * Review the speculative `guardian plan` diff comment on your PR.
   * Merge to `main` to execute `guardian apply` directly into production.
