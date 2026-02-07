<#
.SYNOPSIS
    Azure Deployment Script for Agent Operating System (AOS)
    
.DESCRIPTION
    This PowerShell script orchestrates the complete deployment of the Agent Operating System
    to Azure, including all required infrastructure components:
    - Azure Functions (3 Function Apps)
    - Azure Service Bus (Namespace, Queues, Topics)
    - Azure Storage (Blob, Table, Queue)
    - Azure Key Vault
    - Azure Application Insights
    - Azure Machine Learning Workspace
    - Managed Identities
    
    The script includes:
    - Pre-deployment validation
    - Bi-directional status checking from Azure
    - Idempotent deployment (safe to run multiple times)
    - Comprehensive error handling
    - Detailed logging
    - Post-deployment verification
    
.PARAMETER ResourceGroupName
    Name of the Azure Resource Group to deploy to (will be created if it doesn't exist)
    
.PARAMETER Location
    Azure region for deployment (e.g., 'eastus', 'westus2')
    
.PARAMETER Environment
    Environment name: 'dev', 'staging', or 'prod'
    
.PARAMETER ParametersFile
    Path to the Bicep parameters file (optional, defaults to parameters.{Environment}.json)
    
.PARAMETER SkipPreCheck
    Skip pre-deployment validation checks
    
.PARAMETER SkipPostCheck
    Skip post-deployment verification checks
    
.PARAMETER DeployCode
    Deploy Function App code after infrastructure deployment
    
.PARAMETER Verbose
    Enable verbose output
    
.EXAMPLE
    .\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev"
    
.EXAMPLE
    .\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-prod" -Location "eastus2" -Environment "prod" -DeployCode
    
.NOTES
    Author: Agent Operating System Team
    Version: 1.0.0
    Requires: Azure CLI or Azure PowerShell Module
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$Location,
    
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment,
    
    [Parameter(Mandatory = $false)]
    [string]$ParametersFile = "",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipPreCheck,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipPostCheck,
    
    [Parameter(Mandatory = $false)]
    [switch]$DeployCode,
    
    [Parameter(Mandatory = $false)]
    [switch]$UseAzCli
)

# ============================================================================
# SCRIPT CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Script paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BicepTemplate = Join-Path $ScriptDir "main.bicep"
$DefaultParametersFile = Join-Path $ScriptDir "parameters.$Environment.json"

# Use default parameters file if not specified
if ([string]::IsNullOrEmpty($ParametersFile)) {
    $ParametersFile = $DefaultParametersFile
}

# Deployment configuration
$DeploymentName = "aos-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$LogFile = Join-Path $ScriptDir "deployment-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        'Info'    { Write-Host $logMessage -ForegroundColor White }
        'Warning' { Write-Host $logMessage -ForegroundColor Yellow }
        'Error'   { Write-Host $logMessage -ForegroundColor Red }
        'Success' { Write-Host $logMessage -ForegroundColor Green }
    }
    
    # File output
    Add-Content -Path $LogFile -Value $logMessage
}

function Write-Header {
    param([string]$Title)
    
    $border = "=" * 80
    Write-Log ""
    Write-Log $border
    Write-Log $Title
    Write-Log $border
}

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $allPrereqsMet = $true
    
    # Check Azure CLI or PowerShell Module
    if ($UseAzCli) {
        Write-Log "Checking Azure CLI installation..."
        try {
            $azVersion = az version --output json 2>$null | ConvertFrom-Json
            Write-Log "✓ Azure CLI version: $($azVersion.'azure-cli')" -Level Success
        }
        catch {
            Write-Log "✗ Azure CLI not found. Please install from https://docs.microsoft.com/cli/azure/install-azure-cli" -Level Error
            $allPrereqsMet = $false
        }
    }
    else {
        Write-Log "Checking Azure PowerShell module..."
        $azModule = Get-Module -ListAvailable -Name Az.Accounts
        if ($azModule) {
            Write-Log "✓ Azure PowerShell module version: $($azModule.Version)" -Level Success
        }
        else {
            Write-Log "✗ Azure PowerShell module not found. Install with: Install-Module -Name Az" -Level Error
            $allPrereqsMet = $false
        }
    }
    
    # Check Bicep CLI
    Write-Log "Checking Bicep CLI installation..."
    try {
        if ($UseAzCli) {
            $bicepVersion = az bicep version
        }
        else {
            $bicepVersion = bicep --version 2>$null
        }
        Write-Log "✓ Bicep CLI installed: $bicepVersion" -Level Success
    }
    catch {
        Write-Log "✗ Bicep CLI not found. Installing..." -Level Warning
        if ($UseAzCli) {
            az bicep install
        }
        else {
            Write-Log "Install Bicep from: https://docs.microsoft.com/azure/azure-resource-manager/bicep/install" -Level Error
            $allPrereqsMet = $false
        }
    }
    
    # Check if template file exists
    Write-Log "Checking Bicep template..."
    if (Test-Path $BicepTemplate) {
        Write-Log "✓ Bicep template found: $BicepTemplate" -Level Success
    }
    else {
        Write-Log "✗ Bicep template not found: $BicepTemplate" -Level Error
        $allPrereqsMet = $false
    }
    
    # Check if parameters file exists
    Write-Log "Checking parameters file..."
    if (Test-Path $ParametersFile) {
        Write-Log "✓ Parameters file found: $ParametersFile" -Level Success
    }
    else {
        Write-Log "✗ Parameters file not found: $ParametersFile" -Level Error
        $allPrereqsMet = $false
    }
    
    return $allPrereqsMet
}

# ============================================================================
# AZURE AUTHENTICATION
# ============================================================================

function Initialize-AzureConnection {
    Write-Header "Azure Authentication"
    
    if ($UseAzCli) {
        Write-Log "Checking Azure CLI authentication..."
        try {
            $account = az account show --output json | ConvertFrom-Json
            Write-Log "✓ Authenticated as: $($account.user.name)" -Level Success
            Write-Log "✓ Subscription: $($account.name) ($($account.id))" -Level Success
        }
        catch {
            Write-Log "Not authenticated. Running 'az login'..." -Level Warning
            az login
            $account = az account show --output json | ConvertFrom-Json
            Write-Log "✓ Authenticated as: $($account.user.name)" -Level Success
        }
    }
    else {
        Write-Log "Checking Azure PowerShell authentication..."
        try {
            $context = Get-AzContext
            if ($null -eq $context) {
                throw "Not authenticated"
            }
            Write-Log "✓ Authenticated as: $($context.Account.Id)" -Level Success
            Write-Log "✓ Subscription: $($context.Subscription.Name) ($($context.Subscription.Id))" -Level Success
        }
        catch {
            Write-Log "Not authenticated. Running 'Connect-AzAccount'..." -Level Warning
            Connect-AzAccount
            $context = Get-AzContext
            Write-Log "✓ Authenticated as: $($context.Account.Id)" -Level Success
        }
    }
}

# ============================================================================
# RESOURCE GROUP MANAGEMENT
# ============================================================================

function Initialize-ResourceGroup {
    Write-Header "Resource Group Initialization"
    
    Write-Log "Checking if resource group exists: $ResourceGroupName"
    
    if ($UseAzCli) {
        $rgExists = az group exists --name $ResourceGroupName --output tsv
        
        if ($rgExists -eq "true") {
            Write-Log "✓ Resource group already exists" -Level Success
            
            # Get resource group details
            $rg = az group show --name $ResourceGroupName --output json | ConvertFrom-Json
            Write-Log "  Location: $($rg.location)"
            Write-Log "  Tags: $($rg.tags | ConvertTo-Json -Compress)"
        }
        else {
            Write-Log "Creating resource group..." -Level Warning
            az group create --name $ResourceGroupName --location $Location --output none
            Write-Log "✓ Resource group created successfully" -Level Success
        }
    }
    else {
        $rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
        
        if ($rg) {
            Write-Log "✓ Resource group already exists" -Level Success
            Write-Log "  Location: $($rg.Location)"
            Write-Log "  Tags: $($rg.Tags | ConvertTo-Json -Compress)"
        }
        else {
            Write-Log "Creating resource group..." -Level Warning
            $rg = New-AzResourceGroup -Name $ResourceGroupName -Location $Location
            Write-Log "✓ Resource group created successfully" -Level Success
        }
    }
}

# ============================================================================
# DEPLOYMENT VALIDATION
# ============================================================================

function Test-DeploymentTemplate {
    Write-Header "Template Validation"
    
    Write-Log "Validating Bicep template..."
    
    try {
        if ($UseAzCli) {
            $validation = az deployment group validate `
                --resource-group $ResourceGroupName `
                --template-file $BicepTemplate `
                --parameters "@$ParametersFile" `
                --output json | ConvertFrom-Json
            
            if ($validation.properties.provisioningState -eq "Succeeded") {
                Write-Log "✓ Template validation succeeded" -Level Success
            }
            else {
                Write-Log "✗ Template validation failed" -Level Error
                Write-Log ($validation | ConvertTo-Json -Depth 10)
                return $false
            }
        }
        else {
            $validation = Test-AzResourceGroupDeployment `
                -ResourceGroupName $ResourceGroupName `
                -TemplateFile $BicepTemplate `
                -TemplateParameterFile $ParametersFile
            
            if ($validation.Count -eq 0) {
                Write-Log "✓ Template validation succeeded" -Level Success
            }
            else {
                Write-Log "✗ Template validation failed with errors:" -Level Error
                $validation | ForEach-Object {
                    Write-Log "  - $($_.Message)" -Level Error
                }
                return $false
            }
        }
        
        return $true
    }
    catch {
        Write-Log "✗ Template validation error: $($_.Exception.Message)" -Level Error
        return $false
    }
}

# ============================================================================
# INFRASTRUCTURE DEPLOYMENT
# ============================================================================

function Start-InfrastructureDeployment {
    Write-Header "Infrastructure Deployment"
    
    Write-Log "Starting deployment: $DeploymentName"
    Write-Log "  Resource Group: $ResourceGroupName"
    Write-Log "  Environment: $Environment"
    Write-Log "  Location: $Location"
    Write-Log "  Template: $BicepTemplate"
    Write-Log "  Parameters: $ParametersFile"
    
    try {
        if ($UseAzCli) {
            Write-Log "Deploying infrastructure using Azure CLI..."
            
            $deployment = az deployment group create `
                --name $DeploymentName `
                --resource-group $ResourceGroupName `
                --template-file $BicepTemplate `
                --parameters "@$ParametersFile" `
                --output json | ConvertFrom-Json
            
            if ($deployment.properties.provisioningState -eq "Succeeded") {
                Write-Log "✓ Infrastructure deployment succeeded" -Level Success
                return $deployment.properties.outputs
            }
            else {
                Write-Log "✗ Infrastructure deployment failed" -Level Error
                Write-Log ($deployment | ConvertTo-Json -Depth 10)
                return $null
            }
        }
        else {
            Write-Log "Deploying infrastructure using Azure PowerShell..."
            
            $deployment = New-AzResourceGroupDeployment `
                -Name $DeploymentName `
                -ResourceGroupName $ResourceGroupName `
                -TemplateFile $BicepTemplate `
                -TemplateParameterFile $ParametersFile `
                -Verbose
            
            if ($deployment.ProvisioningState -eq "Succeeded") {
                Write-Log "✓ Infrastructure deployment succeeded" -Level Success
                return $deployment.Outputs
            }
            else {
                Write-Log "✗ Infrastructure deployment failed" -Level Error
                Write-Log ($deployment | ConvertTo-Json -Depth 10)
                return $null
            }
        }
    }
    catch {
        Write-Log "✗ Deployment error: $($_.Exception.Message)" -Level Error
        return $null
    }
}

# ============================================================================
# DEPLOYMENT STATUS VERIFICATION (BI-DIRECTIONAL)
# ============================================================================

function Get-DeploymentStatus {
    param(
        [string]$DeploymentName
    )
    
    Write-Header "Deployment Status Verification"
    
    Write-Log "Retrieving deployment status from Azure..."
    
    try {
        if ($UseAzCli) {
            # Get deployment details
            $deployment = az deployment group show `
                --name $DeploymentName `
                --resource-group $ResourceGroupName `
                --output json | ConvertFrom-Json
            
            Write-Log "Deployment Name: $($deployment.name)"
            Write-Log "Provisioning State: $($deployment.properties.provisioningState)"
            Write-Log "Timestamp: $($deployment.properties.timestamp)"
            Write-Log "Duration: $($deployment.properties.duration)"
            
            # Get resource list
            Write-Log "`nVerifying deployed resources..."
            $resources = az resource list --resource-group $ResourceGroupName --output json | ConvertFrom-Json
            
            Write-Log "`nDeployed Resources ($($resources.Count)):"
            $resourcesByType = $resources | Group-Object -Property type
            foreach ($group in $resourcesByType) {
                Write-Log "  $($group.Name): $($group.Count) resource(s)"
                foreach ($resource in $group.Group) {
                    $status = Get-ResourceProvisioningState -ResourceId $resource.id
                    $statusSymbol = if ($status -eq "Succeeded") { "✓" } else { "✗" }
                    Write-Log "    $statusSymbol $($resource.name) [$status]" -Level $(if ($status -eq "Succeeded") { "Success" } else { "Warning" })
                }
            }
        }
        else {
            # Get deployment details
            $deployment = Get-AzResourceGroupDeployment `
                -ResourceGroupName $ResourceGroupName `
                -Name $DeploymentName
            
            Write-Log "Deployment Name: $($deployment.DeploymentName)"
            Write-Log "Provisioning State: $($deployment.ProvisioningState)"
            Write-Log "Timestamp: $($deployment.Timestamp)"
            Write-Log "Duration: $(($deployment.Timestamp - $deployment.Timestamp.AddSeconds(-$deployment.Duration.TotalSeconds)).ToString())"
            
            # Get resource list
            Write-Log "`nVerifying deployed resources..."
            $resources = Get-AzResource -ResourceGroupName $ResourceGroupName
            
            Write-Log "`nDeployed Resources ($($resources.Count)):"
            $resourcesByType = $resources | Group-Object -Property ResourceType
            foreach ($group in $resourcesByType) {
                Write-Log "  $($group.Name): $($group.Count) resource(s)"
                foreach ($resource in $group.Group) {
                    $fullResource = Get-AzResource -ResourceId $resource.ResourceId
                    $status = $fullResource.Properties.provisioningState
                    if ([string]::IsNullOrEmpty($status)) { $status = "N/A" }
                    $statusSymbol = if ($status -eq "Succeeded" -or $status -eq "N/A") { "✓" } else { "✗" }
                    Write-Log "    $statusSymbol $($resource.Name) [$status]" -Level $(if ($status -eq "Succeeded" -or $status -eq "N/A") { "Success" } else { "Warning" })
                }
            }
        }
        
        return $deployment
    }
    catch {
        Write-Log "✗ Error retrieving deployment status: $($_.Exception.Message)" -Level Error
        return $null
    }
}

function Get-ResourceProvisioningState {
    param([string]$ResourceId)
    
    try {
        if ($UseAzCli) {
            $resource = az resource show --ids $ResourceId --output json 2>$null | ConvertFrom-Json
            if ($resource.properties.provisioningState) {
                return $resource.properties.provisioningState
            }
        }
        return "Succeeded"  # Default if no provisioning state
    }
    catch {
        return "Unknown"
    }
}

# ============================================================================
# POST-DEPLOYMENT VERIFICATION
# ============================================================================

function Test-DeployedResources {
    param($Outputs)
    
    Write-Header "Post-Deployment Verification"
    
    $allTestsPassed = $true
    
    # Test Storage Account
    if ($Outputs.storageAccountName) {
        $storageName = if ($UseAzCli) { $Outputs.storageAccountName.value } else { $Outputs.storageAccountName.Value }
        Write-Log "Testing Storage Account: $storageName"
        
        try {
            if ($UseAzCli) {
                $storage = az storage account show --name $storageName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "  ✓ Storage Account accessible" -Level Success
                Write-Log "    Primary Endpoint: $($storage.primaryEndpoints.blob)"
            }
            else {
                $storage = Get-AzStorageAccount -ResourceGroupName $ResourceGroupName -Name $storageName
                Write-Log "  ✓ Storage Account accessible" -Level Success
                Write-Log "    Primary Endpoint: $($storage.PrimaryEndpoints.Blob)"
            }
        }
        catch {
            Write-Log "  ✗ Storage Account test failed: $($_.Exception.Message)" -Level Error
            $allTestsPassed = $false
        }
    }
    
    # Test Service Bus Namespace
    if ($Outputs.serviceBusNamespaceName) {
        $sbName = if ($UseAzCli) { $Outputs.serviceBusNamespaceName.value } else { $Outputs.serviceBusNamespaceName.Value }
        Write-Log "Testing Service Bus Namespace: $sbName"
        
        try {
            if ($UseAzCli) {
                $sb = az servicebus namespace show --name $sbName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "  ✓ Service Bus Namespace accessible" -Level Success
                Write-Log "    Service Bus Endpoint: $($sb.serviceBusEndpoint)"
                
                # List queues
                $queues = az servicebus queue list --namespace-name $sbName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "    Queues: $($queues.Count)"
                foreach ($queue in $queues) {
                    Write-Log "      - $($queue.name)"
                }
            }
            else {
                $sb = Get-AzServiceBusNamespace -ResourceGroupName $ResourceGroupName -Name $sbName
                Write-Log "  ✓ Service Bus Namespace accessible" -Level Success
                Write-Log "    Service Bus Endpoint: $($sb.ServiceBusEndpoint)"
                
                # List queues
                $queues = Get-AzServiceBusQueue -ResourceGroupName $ResourceGroupName -Namespace $sbName
                Write-Log "    Queues: $($queues.Count)"
                foreach ($queue in $queues) {
                    Write-Log "      - $($queue.Name)"
                }
            }
        }
        catch {
            Write-Log "  ✗ Service Bus test failed: $($_.Exception.Message)" -Level Error
            $allTestsPassed = $false
        }
    }
    
    # Test Key Vault
    if ($Outputs.keyVaultName) {
        $kvName = if ($UseAzCli) { $Outputs.keyVaultName.value } else { $Outputs.keyVaultName.Value }
        Write-Log "Testing Key Vault: $kvName"
        
        try {
            if ($UseAzCli) {
                $kv = az keyvault show --name $kvName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "  ✓ Key Vault accessible" -Level Success
                Write-Log "    Vault URI: $($kv.properties.vaultUri)"
            }
            else {
                $kv = Get-AzKeyVault -ResourceGroupName $ResourceGroupName -VaultName $kvName
                Write-Log "  ✓ Key Vault accessible" -Level Success
                Write-Log "    Vault URI: $($kv.VaultUri)"
            }
        }
        catch {
            Write-Log "  ✗ Key Vault test failed: $($_.Exception.Message)" -Level Error
            $allTestsPassed = $false
        }
    }
    
    # Test Function Apps
    if ($Outputs.functionAppName) {
        $funcName = if ($UseAzCli) { $Outputs.functionAppName.value } else { $Outputs.functionAppName.Value }
        Write-Log "Testing Function App: $funcName"
        
        try {
            if ($UseAzCli) {
                $func = az functionapp show --name $funcName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "  ✓ Function App accessible" -Level Success
                Write-Log "    State: $($func.state)"
                Write-Log "    URL: https://$($func.defaultHostName)"
            }
            else {
                $func = Get-AzWebApp -ResourceGroupName $ResourceGroupName -Name $funcName
                Write-Log "  ✓ Function App accessible" -Level Success
                Write-Log "    State: $($func.State)"
                Write-Log "    URL: https://$($func.DefaultHostName)"
            }
        }
        catch {
            Write-Log "  ✗ Function App test failed: $($_.Exception.Message)" -Level Error
            $allTestsPassed = $false
        }
    }
    
    # Test Application Insights
    if ($Outputs.appInsightsName -and $Outputs.appInsightsName.value) {
        $aiName = if ($UseAzCli) { $Outputs.appInsightsName.value } else { $Outputs.appInsightsName.Value }
        Write-Log "Testing Application Insights: $aiName"
        
        try {
            if ($UseAzCli) {
                $ai = az monitor app-insights component show --app $aiName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
                Write-Log "  ✓ Application Insights accessible" -Level Success
                Write-Log "    Instrumentation Key: $($ai.instrumentationKey.Substring(0, 8))..."
            }
            else {
                $ai = Get-AzApplicationInsights -ResourceGroupName $ResourceGroupName -Name $aiName
                Write-Log "  ✓ Application Insights accessible" -Level Success
                Write-Log "    Instrumentation Key: $($ai.InstrumentationKey.Substring(0, 8))..."
            }
        }
        catch {
            Write-Log "  ✗ Application Insights test failed: $($_.Exception.Message)" -Level Error
            $allTestsPassed = $false
        }
    }
    
    return $allTestsPassed
}

# ============================================================================
# FUNCTION APP CODE DEPLOYMENT
# ============================================================================

function Publish-FunctionAppCode {
    param($Outputs)
    
    Write-Header "Function App Code Deployment"
    
    if (-not $DeployCode) {
        Write-Log "Code deployment skipped (use -DeployCode to enable)" -Level Warning
        return
    }
    
    $funcName = if ($UseAzCli) { $Outputs.functionAppName.value } else { $Outputs.functionAppName.Value }
    Write-Log "Deploying code to Function App: $funcName"
    
    try {
        # Create deployment package
        $deploymentPackage = Join-Path $env:TEMP "aos-deployment.zip"
        Write-Log "Creating deployment package..."
        
        # Get all files to deploy (excluding .git, .github, tests, etc.)
        $filesToDeploy = @(
            "function_app.py",
            "host.json",
            "requirements.txt",
            "src",
            "azure_functions",
            "config"
        )
        
        # Create zip package
        if (Test-Path $deploymentPackage) {
            Remove-Item $deploymentPackage -Force
        }
        
        Push-Location $RepoRoot
        Compress-Archive -Path $filesToDeploy -DestinationPath $deploymentPackage -Force
        Pop-Location
        
        Write-Log "✓ Deployment package created: $deploymentPackage" -Level Success
        
        # Deploy to Azure
        Write-Log "Uploading package to Azure..."
        
        if ($UseAzCli) {
            az functionapp deployment source config-zip `
                --resource-group $ResourceGroupName `
                --name $funcName `
                --src $deploymentPackage `
                --build-remote true
        }
        else {
            Publish-AzWebApp `
                -ResourceGroupName $ResourceGroupName `
                -Name $funcName `
                -ArchivePath $deploymentPackage `
                -Force
        }
        
        Write-Log "✓ Code deployment completed successfully" -Level Success
        
        # Clean up
        Remove-Item $deploymentPackage -Force
    }
    catch {
        Write-Log "✗ Code deployment failed: $($_.Exception.Message)" -Level Error
    }
}

# ============================================================================
# OUTPUT DEPLOYMENT SUMMARY
# ============================================================================

function Write-DeploymentSummary {
    param($Outputs)
    
    Write-Header "Deployment Summary"
    
    if ($null -eq $Outputs) {
        Write-Log "No outputs available" -Level Warning
        return
    }
    
    Write-Log "Deployment Outputs:"
    Write-Log ""
    
    # Helper function to get output value
    function Get-OutputValue($output) {
        if ($UseAzCli) { return $output.value } else { return $output.Value }
    }
    
    # Storage Account
    if ($Outputs.storageAccountName) {
        Write-Log "Storage Account:" -Level Success
        Write-Log "  Name: $(Get-OutputValue $Outputs.storageAccountName)"
        if ($Outputs.storageConnectionString) {
            $connStr = Get-OutputValue $Outputs.storageConnectionString
            Write-Log "  Connection String: $($connStr.Substring(0, 50))..."
        }
    }
    
    # Service Bus
    if ($Outputs.serviceBusNamespaceName) {
        Write-Log "`nService Bus:" -Level Success
        Write-Log "  Namespace: $(Get-OutputValue $Outputs.serviceBusNamespaceName)"
    }
    
    # Key Vault
    if ($Outputs.keyVaultName) {
        Write-Log "`nKey Vault:" -Level Success
        Write-Log "  Name: $(Get-OutputValue $Outputs.keyVaultName)"
        Write-Log "  URI: $(Get-OutputValue $Outputs.keyVaultUri)"
    }
    
    # Function Apps
    if ($Outputs.functionAppName) {
        Write-Log "`nFunction Apps:" -Level Success
        Write-Log "  Main App: $(Get-OutputValue $Outputs.functionAppName)"
        Write-Log "    URL: $(Get-OutputValue $Outputs.functionAppUrl)"
        
        if ($Outputs.mcpServerFunctionAppName) {
            Write-Log "  MCP Server App: $(Get-OutputValue $Outputs.mcpServerFunctionAppName)"
            Write-Log "    URL: $(Get-OutputValue $Outputs.mcpServerFunctionAppUrl)"
        }
        
        if ($Outputs.realmFunctionAppName) {
            Write-Log "  Realm App: $(Get-OutputValue $Outputs.realmFunctionAppName)"
            Write-Log "    URL: $(Get-OutputValue $Outputs.realmFunctionAppUrl)"
        }
    }
    
    # Application Insights
    if ($Outputs.appInsightsName -and (Get-OutputValue $Outputs.appInsightsName)) {
        Write-Log "`nApplication Insights:" -Level Success
        Write-Log "  Name: $(Get-OutputValue $Outputs.appInsightsName)"
    }
    
    # Azure ML
    if ($Outputs.azureMLWorkspaceName -and (Get-OutputValue $Outputs.azureMLWorkspaceName)) {
        Write-Log "`nAzure ML Workspace:" -Level Success
        Write-Log "  Name: $(Get-OutputValue $Outputs.azureMLWorkspaceName)"
    }
    
    Write-Log ""
    Write-Log "Log file: $LogFile" -Level Info
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    $startTime = Get-Date
    
    Write-Header "Agent Operating System - Azure Deployment"
    Write-Log "Started: $startTime"
    Write-Log "Environment: $Environment"
    Write-Log "Resource Group: $ResourceGroupName"
    Write-Log "Location: $Location"
    Write-Log ""
    
    try {
        # Step 1: Prerequisites
        if (-not (Test-Prerequisites)) {
            Write-Log "✗ Prerequisites check failed. Please resolve issues and try again." -Level Error
            exit 1
        }
        
        # Step 2: Azure Authentication
        Initialize-AzureConnection
        
        # Step 3: Resource Group
        Initialize-ResourceGroup
        
        # Step 4: Pre-deployment validation
        if (-not $SkipPreCheck) {
            if (-not (Test-DeploymentTemplate)) {
                Write-Log "✗ Template validation failed. Please fix errors and try again." -Level Error
                exit 1
            }
        }
        else {
            Write-Log "Skipping pre-deployment validation (as requested)" -Level Warning
        }
        
        # Step 5: Deploy Infrastructure
        $outputs = Start-InfrastructureDeployment
        
        if ($null -eq $outputs) {
            Write-Log "✗ Infrastructure deployment failed" -Level Error
            exit 1
        }
        
        # Step 6: Verify Deployment Status (Bi-directional check)
        $deploymentStatus = Get-DeploymentStatus -DeploymentName $DeploymentName
        
        # Step 7: Post-deployment verification
        if (-not $SkipPostCheck) {
            $testsPassed = Test-DeployedResources -Outputs $outputs
            
            if (-not $testsPassed) {
                Write-Log "⚠ Some post-deployment tests failed. Please review." -Level Warning
            }
        }
        else {
            Write-Log "Skipping post-deployment verification (as requested)" -Level Warning
        }
        
        # Step 8: Deploy Function App code (optional)
        if ($DeployCode) {
            Publish-FunctionAppCode -Outputs $outputs
        }
        
        # Step 9: Summary
        Write-DeploymentSummary -Outputs $outputs
        
        $endTime = Get-Date
        $duration = $endTime - $startTime
        
        Write-Header "Deployment Complete"
        Write-Log "✓ Deployment completed successfully!" -Level Success
        Write-Log "Duration: $($duration.ToString('hh\:mm\:ss'))"
        Write-Log "End Time: $endTime"
        
        exit 0
    }
    catch {
        Write-Log "✗ Deployment failed with error: $($_.Exception.Message)" -Level Error
        Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level Error
        exit 1
    }
}

# Execute main function
Main
