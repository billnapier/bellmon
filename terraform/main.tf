terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Service Account for Bellmon Sentinel Container
resource "google_service_account" "sentinel_sa" {
  account_id   = "bellmon-sentinel-sa"
  display_name = "Bellmon Academic Sentinel Service Account"
}

# Cloud Run Job for Unattended Execution
resource "google_cloud_run_v2_job" "sentinel_job" {
  name     = "bellmon-sentinel-job"
  location = var.region

  template {
    template {
      service_account = google_service_account.sentinel_sa.email
      containers {
        image = var.container_image
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }
}
