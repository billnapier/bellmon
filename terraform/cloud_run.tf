resource "google_cloud_run_v2_job" "sentinel_batch_job" {
  name     = "bellmon-sentinel-job"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = google_service_account.sentinel_runner.email

      containers {
        image = "gcr.io/${var.project_id}/bellmon-sentinel:latest"

        resources {
          limits = {
            memory = "2Gi"
            cpu    = "1000m"
          }
        }
      }
    }
  }
}
