resource "google_secret_manager_secret" "canvas_api_token" {
  secret_id = "canvas-api-token"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "powerschool_credentials" {
  secret_id = "powerschool-credentials"
  project   = var.project_id

  replication {
    auto {}
  }
}
