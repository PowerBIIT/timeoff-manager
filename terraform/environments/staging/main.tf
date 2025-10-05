# Staging Environment Configuration

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
  environment  = "staging"
  location     = "westeurope"
  project_name = "timeoff-manager"

  tags = {
    Environment = "Staging"
    Project     = "TimeOff Manager"
    ManagedBy   = "Terraform"
    CostCenter  = "Testing"
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

  # Staging: Medium SKU (similar to production but cheaper)
  sku_name   = "GP_Standard_D2s_v3"  # 2 vCores, 8GB RAM
  storage_mb = 65536  # 64 GB

  admin_username = var.db_admin_username
  admin_password = var.db_admin_password
  database_name  = "timeoffdb"

  # Staging: Extended backup, no HA (to save costs)
  backup_retention_days  = 14
  geo_redundant_backup   = true   # Test geo-redundancy
  enable_ha              = false  # No HA in staging

  tags = local.tags
}

# App Service Module
module "app_service" {
  source = "../../modules/app-service"

  project_name        = local.project_name
  environment         = local.environment
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  # Staging: Standard tier (production-like but cheaper)
  sku_name       = "S1"  # Standard tier
  python_version = "3.9"
  flask_env      = "production"  # Test production settings

  # Database connection
  database_url = module.database.connection_string
  secret_key   = var.secret_key

  # Staging: Always on for testing
  always_on = true

  # No deployment slot in staging
  create_staging_slot = false

  tags = local.tags
}
