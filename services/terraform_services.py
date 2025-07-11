def generate_terraform(config: dict) -> str:
    name = config["platform"]["name"]
    region = config["platform"]["region"]
    rg_name = f"{name}-rg"

    tf = [
        'provider "azurerm" {',
        '  features {}',
        '}',
        '',
        f'resource "azurerm_resource_group" "{rg_name}" {{',
        f'  name     = "{rg_name}"',
        f'  location = "{region}"',
        '}',
        ''
    ]

    # Networking
    networking = config.get("networking", {})
    if networking.get("vnet_required"):
        vnet_name = f"{name}-vnet"
        tf.append(f'resource "azurerm_virtual_network" "{vnet_name}" {{')
        tf.append(f'  name                = "{vnet_name}"')
        tf.append(f'  address_space       = ["{networking["vnet_cidr"]}"]')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append('}')
        tf.append('')

        for subnet in networking.get("subnets", []):
            tf.append(f'resource "azurerm_subnet" "{subnet["name"]}" {{')
            tf.append(f'  name                 = "{subnet["name"]}"')
            tf.append(f'  resource_group_name  = azurerm_resource_group.{rg_name}.name')
            tf.append(f'  virtual_network_name = azurerm_virtual_network.{vnet_name}.name')
            tf.append(f'  address_prefixes     = ["{subnet["cidr"]}"]')
            tf.append('}')
            tf.append('')

    # App Services
    for app in config.get("compute", {}).get("app_services", []):
        plan_name = f'{app["name"]}_plan'
        tf.append(f'resource "azurerm_app_service_plan" "{plan_name}" {{')
        tf.append(f'  name                = "{app["name"]}-plan"')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  sku {{')
        tf.append(f'    tier = "PremiumV2"')
        tf.append(f'    size = "{app["sku"]}"')
        tf.append(f'  }}')
        tf.append('}')
        tf.append('')
        tf.append(f'resource "azurerm_app_service" "{app["name"]}" {{')
        tf.append(f'  name                = "{app["name"]}"')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  app_service_plan_id = azurerm_app_service_plan.{plan_name}.id')
        tf.append('}')
        tf.append('')

    # Virtual Machines
    for vm in config.get("compute", {}).get("virtual_machines", []):
        vm_name = f"{name}-vm"
        tf.append(f'resource "azurerm_network_interface" "{vm_name}_nic" {{')
        tf.append(f'  name                = "{vm_name}-nic"')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  ip_configuration {{')
        tf.append(f'    name                          = "internal"')
        tf.append(f'    subnet_id                     = azurerm_subnet.app-subnet.id')
        tf.append(f'    private_ip_address_allocation = "Dynamic"')
        tf.append(f'  }}')
        tf.append('}')
        tf.append('')
        tf.append(f'resource "azurerm_virtual_machine" "{vm_name}" {{')
        tf.append(f'  name                  = "{vm_name}"')
        tf.append(f'  location              = "{region}"')
        tf.append(f'  resource_group_name   = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  network_interface_ids = [azurerm_network_interface.{vm_name}_nic.id]')
        tf.append(f'  vm_size               = "{vm["size"]}"')
        tf.append('')
        tf.append(f'  os_profile {{')
        tf.append(f'    computer_name  = "{vm_name}"')
        tf.append(f'    admin_username = "adminuser"')
        tf.append(f'    admin_password = "Password1234!"')
        tf.append(f'  }}')
        tf.append(f'  os_profile_linux_config {{')
        tf.append(f'    disable_password_authentication = false')
        tf.append(f'  }}')
        tf.append('')
        tf.append(f'  storage_image_reference {{')
        tf.append(f'    publisher = "Canonical"')
        tf.append(f'    offer     = "UbuntuServer"')
        tf.append(f'    sku       = "18.04-LTS"')
        tf.append(f'    version   = "latest"')
        tf.append(f'  }}')
        tf.append('')
        tf.append(f'  storage_os_disk {{')
        tf.append(f'    name              = "{vm_name}_osdisk"')
        tf.append(f'    caching           = "ReadWrite"')
        tf.append(f'    create_option     = "FromImage"')
        tf.append(f'    managed_disk_type = "Standard_LRS"')
        tf.append(f'  }}')
        tf.append('}')
        tf.append('')

    # Storage Accounts
    for sa in config.get("storage_data", {}).get("blob_storage", []):
        tf.append(f'resource "azurerm_storage_account" "{sa["name"]}" {{')
        tf.append(f'  name                     = "{sa["name"].replace("-", "")}"')
        tf.append(f'  resource_group_name      = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  location                 = "{region}"')
        tf.append(f'  account_tier             = "Standard"')
        tf.append(f'  account_replication_type = "{sa["redundancy"]}"')
        tf.append('}')
        tf.append('')

    # Cosmos DB
    for db in config.get("storage_data", {}).get("databases", []):
        if db["type"] == "CosmosDB":
            tf.append(f'resource "azurerm_cosmosdb_account" "cosmosdb" {{')
            tf.append(f'  name                = "{name}-cosmosdb"')
            tf.append(f'  location            = "{region}"')
            tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
            tf.append(f'  offer_type          = "Standard"')
            tf.append(f'  kind                = "GlobalDocumentDB"')
            tf.append(f'  consistency_policy {{')
            tf.append(f'    consistency_level = "Session"')
            tf.append(f'  }}')
            tf.append(f'  geo_location {{')
            tf.append(f'    location          = "{region}"')
            tf.append(f'    failover_priority = 0')
            tf.append(f'  }}')
            tf.append('}')
            tf.append('')

    # Application Insights (opcional)
    if config.get("monitoring", {}).get("application_insights"):
        tf.append(f'resource "azurerm_application_insights" "appinsights" {{')
        tf.append(f'  name                = "{name}-insights"')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  application_type    = "web"')
        tf.append('}')
        tf.append('')

    # Key Vault (opcional)
    if config.get("security", {}).get("key_vault_needed"):
        tf.append(f'resource "azurerm_key_vault" "main" {{')
        tf.append(f'  name                = "{name}-kv"')
        tf.append(f'  location            = "{region}"')
        tf.append(f'  resource_group_name = azurerm_resource_group.{rg_name}.name')
        tf.append(f'  tenant_id           = "00000000-0000-0000-0000-000000000000"')
        tf.append(f'  sku_name            = "standard"')
        tf.append(f'  soft_delete_enabled = true')
        tf.append('}')
        tf.append('')

    return "\n".join(tf)