# Development Environment Configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  environment = "dev"
  location    = "westeurope"
  project_name = "timeoff-manager"

  tags = {
    Environment = "Development"
    Project     = "TimeOff Manager"
    ManagedBy   = "Terraform"
    CostCenter  = "Development"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.project_name}-rg-${local.environment}"
  location = local.location
  tags     = local.tags
}

# Database Module
module "database" {
  source = "../../modules/database"

  project_name        = local.project_name
  environment         = local.environment
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  # Development: Smallest SKU to save costs
  sku_name   = "B_Standard_B1ms"
  storage_mb = 32768  # 32 GB

  admin_username = var.db_admin_username
  admin_password = var.db_admin_password
  database_name  = "timeoffdb"

  # Development: Minimal backup, no HA
  backup_retention_days  = 7
  geo_redundant_backup   = false
  enable_ha              = false

  # Allow developer IPs (optional)
  allowed_ip_addresses = var.developer_ips

  tags = local.tags
}

# App Service Module
module "app_service" {
  source = "../../modules/app-service"

  project_name        = local.project_name
  environment         = local.environment
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  # Development: Free/Basic tier
  sku_name       = "B1"  # Basic tier (lowest cost with always-on)
  python_version = "3.9"
  flask_env      = "development"

  # Database connection
  database_url = module.database.connection_string
  secret_key   = var.secret_key

  # Development: Can turn off to save costs
  always_on = false

  # No staging slot for dev
  create_staging_slot = false

  tags = local.tags
}
