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
  description = "PostgreSQL SKU (e.g., B_Standard_B1ms, GP_Standard_D2s_v3)"
  type        = string
}

variable "storage_mb" {
  description = "Storage size in MB"
  type        = number
}

variable "admin_username" {
  description = "Database admin username"
  type        = string
  sensitive   = true
}

variable "admin_password" {
  description = "Database admin password"
  type        = string
  sensitive   = true
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "timeoffdb"
}

variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "geo_redundant_backup" {
  description = "Enable geo-redundant backups"
  type        = bool
  default     = false
}

variable "enable_ha" {
  description = "Enable High Availability (zone redundant)"
  type        = bool
  default     = false
}

variable "allowed_ip_addresses" {
  description = "List of IP addresses allowed to connect"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
