# App Service Module

resource "azurerm_service_plan" "main" {
  name                = "${var.project_name}-plan-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name           = var.sku_name

  tags = var.tags
}

resource "azurerm_linux_web_app" "main" {
  name                = "${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  service_plan_id     = azurerm_service_plan.main.id

  site_config {
    always_on = var.always_on

    application_stack {
      python_version = var.python_version
    }

    # Security headers
    http2_enabled       = true
    ftps_state         = "FtpsOnly"
    minimum_tls_version = "1.2"
  }

  app_settings = {
    "FLASK_ENV"                = var.flask_env
    "DATABASE_URL"             = var.database_url
    "SECRET_KEY"               = var.secret_key
    "APP_NAME"                 = "${var.project_name}-${var.environment}"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS" = "7"
  }

  https_only = true

  identity {
    type = "SystemAssigned"
  }

  logs {
    application_logs {
      file_system_level = "Information"
    }

    http_logs {
      file_system {
        retention_in_days = 7
        retention_in_mb   = 35
      }
    }
  }

  tags = var.tags
}

# Deployment slot for staging (production only)
resource "azurerm_linux_web_app_slot" "staging" {
  count          = var.create_staging_slot ? 1 : 0
  name           = "staging"
  app_service_id = azurerm_linux_web_app.main.id

  site_config {
    always_on = false

    application_stack {
      python_version = var.python_version
    }

    http2_enabled       = true
    minimum_tls_version = "1.2"
  }

  app_settings = azurerm_linux_web_app.main.app_settings

  tags = var.tags
}
