# PostgreSQL Flexible Server Module

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-db-${var.environment}"
  location               = var.location
  resource_group_name    = var.resource_group_name

  administrator_login    = var.admin_username
  administrator_password = var.admin_password

  sku_name   = var.sku_name
  storage_mb = var.storage_mb
  version    = "13"

  backup_retention_days        = var.backup_retention_days
  geo_redundant_backup_enabled = var.geo_redundant_backup

  # High availability for production
  dynamic "high_availability" {
    for_each = var.enable_ha ? [1] : []
    content {
      mode = "ZoneRedundant"
    }
  }

  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Firewall rule to allow Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Optional: Allow specific IP addresses (for development)
resource "azurerm_postgresql_flexible_server_firewall_rule" "allowed_ips" {
  for_each         = toset(var.allowed_ip_addresses)
  name             = "AllowIP-${replace(each.value, ".", "-")}"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = each.value
  end_ip_address   = each.value
}

# Configuration for SSL enforcement
resource "azurerm_postgresql_flexible_server_configuration" "ssl" {
  name      = "require_secure_transport"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "on"
}
