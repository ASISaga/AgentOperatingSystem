using '../main-modular.bicep'

param environment = 'staging'
param location = 'eastus'
param locationML = 'eastus2'
param projectName = 'aos'
param tags = {
  project: 'AgentOperatingSystem'
  environment: 'staging'
  managedBy: 'bicep'
}
