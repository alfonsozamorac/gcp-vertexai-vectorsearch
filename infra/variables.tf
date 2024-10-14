variable "project_id" {
  description = "Project ID"
  type        = string
}

variable "region" {
  description = "Location"
  type        = string
  default     = "europe-west4"
}

variable "create_cloudrun" {
  description = "Create Cloud Run"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Tags"
  type        = map(string)
  default = {
    "owner" = "alfonsozamora"
  }
}
