output "job_name" {
  value       = google_cloud_run_v2_job.sentinel_job.name
  description = "Cloud Run Job name for Bellmon Sentinel"
}

output "service_account_email" {
  value       = google_service_account.sentinel_sa.email
  description = "Service account email executing Cloud Run Job"
}
