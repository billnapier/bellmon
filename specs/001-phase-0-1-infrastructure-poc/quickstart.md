# Quickstart Guide: Micro-Spec 0.1 Infrastructure & Guardian CI/CD Foundation

**Feature Branch**: `001-phase-0-1-infrastructure-poc`

---

## 1. Local Prerequisites

Ensure the following tools are installed on your workstation:
* **Python 3.11+**: `python3 --version`
* **Terraform 1.5+**: `terraform --version`
* **Google Cloud SDK (`gcloud`)**: `gcloud --version`

---

## 2. Environment Setup

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
   git commit -m "feat(infra): add baseline terraform and guardian workflow"
   git push origin 001-phase-0-1-infrastructure-poc
   ```

2. **Open Pull Request**:
   * Creating a PR triggers `.github/workflows/guardian.yml`.
   * Review the speculative `guardian plan` diff comment on your PR.
   * Merge to `main` to execute `guardian apply` directly into production.
