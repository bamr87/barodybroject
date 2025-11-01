// Minimal PostgreSQL Configuration for Cost Optimization
param serverName string
param location string = resourceGroup().location
param tags object = {}

param databaseUser string = 'psqladmin'
param databaseName string = 'barodydb'
@secure()
param databasePassword string

param allowAllIPsFirewall bool = false

resource postgreServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-01-20-preview' = {
  location: location
  tags: tags
  name: serverName
  sku: {
    name: 'Standard_B1ms'  // Burstable tier - most economical
    tier: 'Burstable'
  }
  properties: {
    version: '13'
    administratorLogin: databaseUser
    administratorLoginPassword: databasePassword
    storage: {
      storageSizeGB: 32  // Minimum size to reduce costs
    }
    backup: {
      backupRetentionDays: 7  // Minimum retention
      geoRedundantBackup: 'Disabled'  // Save costs on geo-redundancy
    }
    highAvailability: {
      mode: 'Disabled'  // No HA for cost savings
    }
  }

  resource firewall_all 'firewallRules' = if (allowAllIPsFirewall) {
    name: 'allow-all-IPs'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '255.255.255.255'
    }
  }
  
  // Allow Azure services to connect
  resource firewall_azure 'firewallRules' = {
    name: 'allow-azure-services'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '0.0.0.0'
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2022-01-20-preview' = {
  parent: postgreServer
  name: databaseName
}

output databaseHost string = postgreServer.properties.fullyQualifiedDomainName
output databaseName string = databaseName
output databaseUser string = databaseUser
