variable "db_admin_username" {
  description = "Database admin username"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_admin_password" {
  description = "Database admin password - MUST be strong for production"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_admin_password) >= 16
    error_message = "Production database password must be at least 16 characters long."
  }
}

variable "secret_key" {
  description = "Flask SECRET_KEY - MUST be unique for production"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.secret_key) >= 32
    error_message = "Production SECRET_KEY must be at least 32 characters long."
  }
}
