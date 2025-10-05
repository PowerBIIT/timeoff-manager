# Production Environment Configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Recommended: Use remote state for production
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstate"
  #   container_name       = "tfstate"
  #   key                  = "timeoff-manager-prod.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

locals {
  environment  = "prod"
  location     = "westeurope"
  project_name = "timeoff-manager"

  tags = {
    Environment = "Production"
    Project     = "TimeOff Manager"
    ManagedBy   = "Terraform"
    CostCenter  = "Production"
    Critical    = "true"
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

  # Production: High-performance SKU
  sku_name   = "GP_Standard_D4s_v3"  # 4 vCores, 16GB RAM
  storage_mb = 131072  # 128 GB

  admin_username = var.db_admin_username
  admin_password = var.db_admin_password
  database_name  = "timeoffdb"

  # Production: Extended backup with geo-redundancy and HA
  backup_retention_days  = 35  # 5 weeks
  geo_redundant_backup   = true
  enable_ha              = true  # Zone-redundant HA

  tags = local.tags
}

# App Service Module
module "app_service" {
  source = "../../modules/app-service"

  project_name        = local.project_name
  environment         = local.environment
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name

  # Production: Premium tier for performance and features
  sku_name       = "P1v2"  # Premium v2 (210 ACU, 3.5GB RAM)
  python_version = "3.9"
  flask_env      = "production"

  # Database connection
  database_url = module.database.connection_string
  secret_key   = var.secret_key

  # Production: Always on required
  always_on = true

  # Production: Create staging slot for blue-green deployments
  create_staging_slot = true

  tags = local.tags
}

# Application Insights for monitoring
resource "azurerm_application_insights" "main" {
  name                = "${local.project_name}-insights-${local.environment}"
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  retention_in_days   = 90

  tags = local.tags
}

# Optional: Azure Key Vault for secrets management
resource "azurerm_key_vault" "main" {
  name                = "${local.project_name}-kv-${local.environment}"
  location            = local.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  enabled_for_deployment          = true
  enabled_for_template_deployment = true
  purge_protection_enabled        = true

  tags = local.tags
}

# Grant App Service access to Key Vault
resource "azurerm_key_vault_access_policy" "app_service" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.app_service.app_service_identity_principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}

data "azurerm_client_config" "current" {}
