{
  "platform": {
    "name": "liberty-ai-backend",
    "environment": "dev",
    "region": "eastus"
  },
  "networking": {
    "vnet_required": true,
    "vnet_cidr": "10.0.0.0/16",
    "subnets": [
      {
        "name": "app-subnet",
        "cidr": "10.0.1.0/24",
        "type": "app",
        "nsg_attached": true
      },
      {
        "name": "db-subnet",
        "cidr": "10.0.2.0/24",
        "type": "db",
        "nsg_attached": true
      }
    ],
    "hub_spoke": false,
    "vpn_gateway": false,
    "firewall_required": false,
    "private_dns_zones": [
      "blob.core.windows.net",
      "database.windows.net"
    ]
  },
  "identity_access": {
    "aad_integration": true,
    "rbac_assignments": [
      {
        "principal_type": "group",
        "role": "Contributor",
        "scope": "subscription"
      }
    ],
    "managed_identities": "system-assigned"
  },
  "compute": {
    "app_services": [
      {
        "name": "backend-app",
        "sku": "P1v2",
        "runtime": "dotnet"
      }
    ],
    "azure_functions": [
      {
        "name": "trigger-fn",
        "plan_type": "consumption",
        "runtime": "python",
        "triggers": ["HTTP"]
      }
    ],
    "virtual_machines": [
      {
        "count": 1,
        "size": "Standard_B2s",
        "os": "Linux",
        "auto_shutdown": true,
        "public_ip": false
      }
    ]
  },
  "storage_data": {
    "blob_storage": [
      {
        "name": "logs-storage",
        "redundancy": "LRS",
        "access_tier": "Hot"
      }
    ],
    "databases": [
      {
        "type": "CosmosDB",
        "tier": "Standard",
        "private_endpoint": true,
        "backup_policy": "Geo-Redundant"
      }
    ]
  },
  "ci_cd": {
    "terraform_state_backend": "Azure Storage",
    "ci_cd_tool": "GitHub Actions",
    "state_locking_enabled": true,
    "secret_management": "Azure Key Vault"
  },
  "monitoring": {
    "log_analytics_workspace": true,
    "retention_days": 90,
    "application_insights": true,
    "diagnostic_settings": true,
    "alerts": [
      {
        "type": "CPU",
        "threshold_percent": 80,
        "email_recipients": ["ops@example.com"]
      }
    ]
  },
  "security": {
    "azure_policy_definitions": ["deny-public-ip", "allowed-skus"],
    "key_vault_needed": true,
    "key_vault_soft_delete": true,
    "key_vault_access_policies_defined": true,
    "security_center_tier": "Standard"
  },
  "tags_naming": {
    "naming_convention": "{env}-{service}-{region}",
    "tags": {
      "environment": "dev",
      "owner": "ai-team",
      "cost_center": "R&D-123"
    }
  }
}