variable "db_admin_username" {
  description = "Database admin username"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}

variable "db_admin_password" {
  description = "Database admin password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask SECRET_KEY"
  type        = string
  sensitive   = true
}
