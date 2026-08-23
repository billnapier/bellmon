resource "google_service_account" "sentinel_runner" {
  account_id   = "bellmon-sentinel-runner"
  display_name = "Bellmon Academic Sentinel Cloud Run Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.sentinel_runner.email}"
}

resource "google_project_iam_member" "artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.sentinel_runner.email}"
}

resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.sentinel_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "canvas_token_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.canvas_api_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.sentinel_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "powerschool_creds_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.powerschool_credentials.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.sentinel_runner.email}"
}
