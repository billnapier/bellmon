resource "google_cloud_run_v2_job" "sentinel_batch_job" {
  name     = "bellmon-sentinel-job"
  location = var.region
  project  = var.project_id

  template {
    template {
      service_account = google_service_account.sentinel_runner.email

      containers {
        image = var.container_image

        resources {
          limits = {
            memory = "2Gi"
            cpu    = "1000m"
          }
        }

        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
      }
    }
  }
}
