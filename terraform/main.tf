
    provider "azurerm" {
    features {}
    }

    resource "azurerm_resource_group" "liberty-ai-backend-rg" {
    name     = "liberty-ai-backend-rg"
    location = "eastus"
    }
    
    resource "azurerm_virtual_network" "liberty-ai-backend-vnet" {
    name                = "liberty-ai-backend-vnet"
    address_space       = ["10.0.0.0/16"]
    location            = "eastus"
    resource_group_name = azurerm_resource_group.liberty-ai-backend-rg.name
    }
    
    resource "azurerm_subnet" "app-subnet" {
    name                 = "app-subnet"
    resource_group_name  = azurerm_resource_group.liberty-ai-backend-rg.name
    virtual_network_name = azurerm_virtual_network.liberty-ai-backend-vnet.name
    address_prefixes     = ["10.0.1.0/24"]
    }
    
    resource "azurerm_subnet" "db-subnet" {
    name                 = "db-subnet"
    resource_group_name  = azurerm_resource_group.liberty-ai-backend-rg.name
    virtual_network_name = azurerm_virtual_network.liberty-ai-backend-vnet.name
    address_prefixes     = ["10.0.2.0/24"]
    }
    
    resource "azurerm_app_service_plan" "backend-app_plan" {
    name                = "backend-app-plan"
    location            = "eastus"
    resource_group_name = azurerm_resource_group.liberty-ai-backend-rg.name
    sku {
        tier = "PremiumV2"
        size = "P1v2"
    }
    }

    resource "azurerm_app_service" "backend-app" {
    name                = "backend-app"
    location            = "eastus"
    resource_group_name = azurerm_resource_group.liberty-ai-backend-rg.name
    app_service_plan_id = azurerm_app_service_plan.backend-app_plan.id
    }
    
    resource "azurerm_virtual_machine" "liberty-ai-backend-vm" {
    name                  = "liberty-ai-backend-vm"
    location              = "eastus"
    resource_group_name   = azurerm_resource_group.liberty-ai-backend-rg.name
    network_interface_ids = []
    vm_size               = "Standard_B2s"

    os_profile {
        computer_name  = "liberty-ai-backend-vm"
        admin_username = "adminuser"
        admin_password = "Password1234!"
    }

    os_profile_linux_config {
        disable_password_authentication = false
    }

    storage_image_reference {
        publisher = "Canonical"
        offer     = "UbuntuServer"
        sku       = "18.04-LTS"
        version   = "latest"
    }

    storage_os_disk {
        name              = "liberty-ai-backend-vm_osdisk"
        caching           = "ReadWrite"
        create_option     = "FromImage"
        managed_disk_type = "Standard_LRS"
    }
    }
    
    resource "azurerm_storage_account" "logs-storage" {
    name                     = "logsstorage"
    resource_group_name      = azurerm_resource_group.liberty-ai-backend-rg.name
    location                 = "eastus"
    account_tier             = "Standard"
    account_replication_type = "LRS"
    }
    
    resource "azurerm_cosmosdb_account" "cosmosdb" {
    name                = "liberty-ai-backend-cosmosdb"
    location            = "eastus"
    resource_group_name = azurerm_resource_group.liberty-ai-backend-rg.name
    offer_type          = "Standard"
    kind                = "GlobalDocumentDB"
    consistency_policy {
        consistency_level = "Session"
    }
    geo_location {
        location          = "eastus"
        failover_priority = 0
    }
    }
    