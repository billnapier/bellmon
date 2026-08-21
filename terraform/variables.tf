variable "project_id" {
  type        = string
  description = "GCP Project ID for Bellmon"
  default     = "bellmon-prod"
}

variable "region" {
  type        = string
  description = "GCP Region for Cloud Run and Cloud Scheduler"
  default     = "us-central1"
}

variable "container_image" {
  type        = string
  description = "Container image URL for Bellmon Sentinel"
  default     = "gcr.io/bellmon-prod/sentinel:latest"
}
