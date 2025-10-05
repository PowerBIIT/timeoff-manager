variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "sku_name" {
  description = "App Service Plan SKU (e.g., B1, S1, P1v2)"
  type        = string
}

variable "python_version" {
  description = "Python version"
  type        = string
  default     = "3.9"
}

variable "flask_env" {
  description = "Flask environment (development/production)"
  type        = string
  default     = "production"
}

variable "database_url" {
  description = "PostgreSQL connection string"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask SECRET_KEY"
  type        = string
  sensitive   = true
}

variable "always_on" {
  description = "Keep app always on (required for production)"
  type        = bool
  default     = true
}

variable "create_staging_slot" {
  description = "Create staging deployment slot"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
