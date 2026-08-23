# Quickstart Guide: Phase 0.4 Containerized Batch Runner & Infrastructure

## Local Batch Runner Execution

1. **Environment Setup**:
   ```bash
   export GCP_PROJECT_ID=$(gcloud config get-value project)
   export CANVAS_API_TOKEN="mock_canvas_token"
   export POWERSCHOOL_USERNAME="test_user"
   export POWERSCHOOL_PASSWORD="test_password"
   ```

2. **Execute Unified Batch Orchestrator**:
   ```bash
   python -m src.main
   ```

3. **Execute Unit Tests**:
   ```bash
   pytest tests/test_main.py -v
   ```

## Docker Container Build & Local Test

1. **Build Container Image**:
   ```bash
   docker build -t bellmon-batch-runner:latest .
   ```

2. **Run Container Locally**:
   ```bash
   docker run --rm \
     -e CANVAS_API_TOKEN="$CANVAS_API_TOKEN" \
     -e POWERSCHOOL_USERNAME="$POWERSCHOOL_USERNAME" \
     -e POWERSCHOOL_PASSWORD="$POWERSCHOOL_PASSWORD" \
     bellmon-batch-runner:latest
   ```

## Infrastructure Validation

1. **Initialize & Validate Terraform**:
   ```bash
   cd terraform
   terraform init -backend=false
   terraform validate
   ```
