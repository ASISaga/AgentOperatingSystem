using '../main-modular.bicep'

param environment = 'prod'
param location = 'eastus'
param locationML = 'eastus2'
param projectName = 'aos'
param tags = {
  project: 'AgentOperatingSystem'
  environment: 'prod'
  managedBy: 'bicep'
  costCenter: 'infrastructure'
}
