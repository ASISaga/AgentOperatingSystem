using '../main-modular.bicep'

param environment = 'dev'
param location = 'eastus'
param locationML = 'eastus'
param projectName = 'aos'
param tags = {
  project: 'AgentOperatingSystem'
  environment: 'dev'
  managedBy: 'bicep'
}
