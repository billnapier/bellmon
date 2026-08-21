# Daily Weekday Sync Cron Job (5:00 PM Mon-Fri)
resource "google_cloud_scheduler_job" "daily_sync" {
  name        = "bellmon-daily-sync-cron"
  description = "Triggers Bellmon academic sync run at 5:00 PM Mon-Fri"
  schedule    = "0 17 * * 1-5"
  time_zone   = "America/Los_Angeles"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.io/v2/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.sentinel_job.name}:run"

    oidc_token {
      service_account_email = google_service_account.sentinel_sa.email
    }
  }
}

# Sunday Digest Cron Job (6:00 PM Sunday)
resource "google_cloud_scheduler_job" "sunday_digest" {
  name        = "bellmon-sunday-digest-cron"
  description = "Triggers Bellmon Sunday digest builder at 6:00 PM Sunday"
  schedule    = "0 18 * * 0"
  time_zone   = "America/Los_Angeles"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.io/v2/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.sentinel_job.name}:run"

    oidc_token {
      service_account_email = google_service_account.sentinel_sa.email
    }
  }
}
