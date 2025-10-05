output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "app_service_url" {
  description = "App Service URL"
  value       = module.app_service.app_service_url
}

output "database_server" {
  description = "Database server FQDN"
  value       = module.database.server_fqdn
}

output "database_name" {
  description = "Database name"
  value       = module.database.database_name
}

output "connection_string" {
  description = "Database connection string"
  value       = module.database.connection_string
  sensitive   = true
}

output "application_insights_key" {
  description = "Application Insights Instrumentation Key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}
