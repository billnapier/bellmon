variable "project_id" {
  type        = string
  description = "Google Cloud Platform Project ID"
  default     = "bellmon-prod"
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
