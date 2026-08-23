# Quickstart Guide: Micro-Spec 0.1 Infrastructure & Guardian CI/CD Foundation

**Feature Branch**: `001-phase-0-1-infrastructure-poc`

---

## 1. Zero-Edit GCP & GitHub Workload Identity Setup Script

Per Constitution v1.2.1, copy and paste this complete script directly into your terminal. It dynamically derives your GCP project number and outputs the exact secret value for GitHub:

```bash
# Set active GCP Project ID
export GCP_PROJECT_ID="bellmon-prod"
gcloud config set project "$GCP_PROJECT_ID"

# Dynamically resolve GCP Project Number
export GCP_PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)")
echo "Selected Project: $GCP_PROJECT_ID (Number: $GCP_PROJECT_NUMBER)"

# Enable required GCP APIs
gcloud services enable iamcredentials.googleapis.com cloudresourcemanager.googleapis.com

# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Bind Service Account to GitHub Repository
gcloud iam service-accounts add-iam-policy-binding "bellmon-sentinel-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${GCP_PROJECT_NUMBER}/locations/global/workload-identity-pools/github-pool/attribute.repository/billnapier/bellmon"

echo ""
echo "=== COPY THIS VALUE FOR GCP_WORKLOAD_IDENTITY_PROVIDER IN GITHUB ==="
gcloud iam workload-identity-pools providers describe "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
```

---

## 2. GitHub Secrets Setup

Add the 2 secrets in GitHub (**Settings > Secrets and variables > Actions**):

| Secret Name | Value |
| :--- | :--- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Output string printed by the script above |
| `GCP_SERVICE_ACCOUNT` | `bellmon-sentinel-runner@bellmon-prod.iam.gserviceaccount.com` |

---

## 3. Local Workstation Validation

```bash
# Python unit tests
pytest tests/test_sanity.py

# Terraform HCL format & validation
cd terraform
terraform init -backend=false
terraform fmt -check
terraform validate
```
