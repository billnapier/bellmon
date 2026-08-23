resource "google_cloud_scheduler_job" "sentinel_batch_schedule" {
  name        = "bellmon-sentinel-schedule"
  description = "Triggers Bellmon Academic Sentinel Cloud Run Job sub-daily (5 PM weekdays)"
  schedule    = "0 17 * * 1-5"
  time_zone   = "America/Los_Angeles"
  project     = var.project_id
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.sentinel_batch_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.sentinel_runner.email
    }
  }
}
