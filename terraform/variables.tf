variable "project_id" {
  type        = string
  description = "Google Cloud Platform Project ID"
  default     = "bellmon"
}

variable "region" {
  type        = string
  description = "Primary GCP Region"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Environment tier"
  default     = "prod"
}

variable "container_image" {
  type        = string
  description = "Container image URL in GCP Artifact Registry"
  default     = "us-central1-docker.pkg.dev/bellmon/bellmon-repo/batch-runner:latest"
}
