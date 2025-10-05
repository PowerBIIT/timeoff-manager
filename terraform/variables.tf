# Variables for TimeOff Manager Infrastructure

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "timeoff-manager"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "TimeOff Manager"
    ManagedBy   = "Terraform"
    Application = "timeoff-manager"
  }
}

# App Service Configuration
variable "app_service_sku" {
  description = "App Service Plan SKU"
  type = object({
    tier = string
    size = string
  })
}

variable "python_version" {
  description = "Python version for App Service"
  type        = string
  default     = "3.9"
}

# Database Configuration
variable "db_sku_name" {
  description = "PostgreSQL SKU"
  type        = string
}

variable "db_storage_mb" {
  description = "Database storage in MB"
  type        = number
}

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

# Backup Configuration
variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "enable_monitoring" {
  description = "Enable Application Insights"
  type        = bool
  default     = true
}
