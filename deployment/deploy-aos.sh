#!/bin/bash

################################################################################
# Azure Deployment Script for Agent Operating System (AOS)
#
# This bash script orchestrates the complete deployment of the Agent Operating
# System to Azure, including all required infrastructure components:
# - Azure Functions (3 Function Apps)
# - Azure Service Bus (Namespace, Queues, Topics)
# - Azure Storage (Blob, Table, Queue)
# - Azure Key Vault
# - Azure Application Insights
# - Azure Machine Learning Workspace
# - Managed Identities
#
# The script includes:
# - Pre-deployment validation
# - Bi-directional status checking from Azure
# - Idempotent deployment (safe to run multiple times)
# - Comprehensive error handling
# - Detailed logging
# - Post-deployment verification
#
# Usage:
#   ./deploy-aos.sh -g <resource-group> -l <location> -e <environment> [options]
#
# Options:
#   -g, --resource-group    Azure Resource Group name (required)
#   -l, --location          Azure region (e.g., eastus, westus2) (required)
#   -e, --environment       Environment (dev, staging, prod) (required)
#   -p, --parameters        Path to parameters file (optional)
#   -c, --deploy-code       Deploy Function App code after infrastructure
#   --skip-pre-check        Skip pre-deployment validation
#   --skip-post-check       Skip post-deployment verification
#   -h, --help              Show this help message
#
# Examples:
#   ./deploy-aos.sh -g rg-aos-dev -l eastus -e dev
#   ./deploy-aos.sh -g rg-aos-prod -l eastus2 -e prod -c
#
# Author: Agent Operating System Team
# Version: 1.0.0
# Requires: Azure CLI (az), Bicep CLI
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# SCRIPT CONFIGURATION
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BICEP_TEMPLATE="$SCRIPT_DIR/main.bicep"

# Default values
RESOURCE_GROUP=""
LOCATION=""
ENVIRONMENT=""
PARAMETERS_FILE=""
DEPLOY_CODE=false
SKIP_PRE_CHECK=false
SKIP_POST_CHECK=false

# Deployment configuration
DEPLOYMENT_NAME="aos-deployment-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$SCRIPT_DIR/deployment-$(date +%Y%m%d-%H%M%S).log"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log_info() {
    local msg="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${BLUE}[$timestamp] [INFO]${NC} $msg" | tee -a "$LOG_FILE"
}

log_success() {
    local msg="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${GREEN}[$timestamp] [SUCCESS]${NC} $msg" | tee -a "$LOG_FILE"
}

log_warning() {
    local msg="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${YELLOW}[$timestamp] [WARNING]${NC} $msg" | tee -a "$LOG_FILE"
}

log_error() {
    local msg="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "${RED}[$timestamp] [ERROR]${NC} $msg" | tee -a "$LOG_FILE"
}

log_header() {
    local title="$1"
    local border="================================================================================"
    echo "" | tee -a "$LOG_FILE"
    echo "$border" | tee -a "$LOG_FILE"
    echo "$title" | tee -a "$LOG_FILE"
    echo "$border" | tee -a "$LOG_FILE"
}

# ============================================================================
# HELP FUNCTION
# ============================================================================

show_help() {
    cat << EOF
Azure Deployment Script for Agent Operating System (AOS)

Usage: $0 -g <resource-group> -l <location> -e <environment> [options]

Required Arguments:
  -g, --resource-group    Azure Resource Group name
  -l, --location          Azure region (e.g., eastus, westus2)
  -e, --environment       Environment (dev, staging, prod)

Optional Arguments:
  -p, --parameters        Path to parameters file
  -c, --deploy-code       Deploy Function App code after infrastructure
  --skip-pre-check        Skip pre-deployment validation
  --skip-post-check       Skip post-deployment verification
  -h, --help              Show this help message

Examples:
  $0 -g rg-aos-dev -l eastus -e dev
  $0 -g rg-aos-prod -l eastus2 -e prod -c

EOF
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -g|--resource-group)
                RESOURCE_GROUP="$2"
                shift 2
                ;;
            -l|--location)
                LOCATION="$2"
                shift 2
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
                    log_error "Environment must be: dev, staging, or prod"
                    exit 1
                fi
                shift 2
                ;;
            -p|--parameters)
                PARAMETERS_FILE="$2"
                shift 2
                ;;
            -c|--deploy-code)
                DEPLOY_CODE=true
                shift
                ;;
            --skip-pre-check)
                SKIP_PRE_CHECK=true
                shift
                ;;
            --skip-post-check)
                SKIP_POST_CHECK=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate required arguments
    if [[ -z "$RESOURCE_GROUP" ]] || [[ -z "$LOCATION" ]] || [[ -z "$ENVIRONMENT" ]]; then
        log_error "Missing required arguments"
        show_help
        exit 1
    fi
    
    # Set default parameters file if not specified
    if [[ -z "$PARAMETERS_FILE" ]]; then
        PARAMETERS_FILE="$SCRIPT_DIR/parameters.$ENVIRONMENT.json"
    fi
}

# ============================================================================
# PREREQUISITE CHECKS
# ============================================================================

check_prerequisites() {
    log_header "Checking Prerequisites"
    
    local all_prereqs_met=true
    
    # Check Azure CLI
    log_info "Checking Azure CLI installation..."
    if command -v az &> /dev/null; then
        local az_version=$(az version --output json | jq -r '."azure-cli"')
        log_success "✓ Azure CLI version: $az_version"
    else
        log_error "✗ Azure CLI not found. Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
        all_prereqs_met=false
    fi
    
    # Check Bicep CLI
    log_info "Checking Bicep CLI installation..."
    if az bicep version &> /dev/null; then
        local bicep_version=$(az bicep version)
        log_success "✓ Bicep CLI installed: $bicep_version"
    else
        log_warning "✗ Bicep CLI not found. Installing..."
        az bicep install
        log_success "✓ Bicep CLI installed"
    fi
    
    # Check jq for JSON processing
    log_info "Checking jq installation..."
    if command -v jq &> /dev/null; then
        log_success "✓ jq installed"
    else
        log_warning "✗ jq not found. Some features may not work. Install with: apt-get install jq (Ubuntu) or brew install jq (Mac)"
    fi
    
    # Check Bicep template file
    log_info "Checking Bicep template..."
    if [[ -f "$BICEP_TEMPLATE" ]]; then
        log_success "✓ Bicep template found: $BICEP_TEMPLATE"
    else
        log_error "✗ Bicep template not found: $BICEP_TEMPLATE"
        all_prereqs_met=false
    fi
    
    # Check parameters file
    log_info "Checking parameters file..."
    if [[ -f "$PARAMETERS_FILE" ]]; then
        log_success "✓ Parameters file found: $PARAMETERS_FILE"
    else
        log_error "✗ Parameters file not found: $PARAMETERS_FILE"
        all_prereqs_met=false
    fi
    
    if [[ "$all_prereqs_met" == false ]]; then
        return 1
    fi
    
    return 0
}

# ============================================================================
# AZURE AUTHENTICATION
# ============================================================================

initialize_azure_connection() {
    log_header "Azure Authentication"
    
    log_info "Checking Azure CLI authentication..."
    
    if az account show &> /dev/null; then
        local account_name=$(az account show --query name -o tsv)
        local account_id=$(az account show --query id -o tsv)
        local user_name=$(az account show --query user.name -o tsv)
        
        log_success "✓ Authenticated as: $user_name"
        log_success "✓ Subscription: $account_name ($account_id)"
    else
        log_warning "Not authenticated. Running 'az login'..."
        az login
        
        local account_name=$(az account show --query name -o tsv)
        local user_name=$(az account show --query user.name -o tsv)
        log_success "✓ Authenticated as: $user_name"
        log_success "✓ Subscription: $account_name"
    fi
}

# ============================================================================
# RESOURCE GROUP MANAGEMENT
# ============================================================================

initialize_resource_group() {
    log_header "Resource Group Initialization"
    
    log_info "Checking if resource group exists: $RESOURCE_GROUP"
    
    if az group exists --name "$RESOURCE_GROUP" --output tsv | grep -q "true"; then
        log_success "✓ Resource group already exists"
        
        # Get resource group details
        local rg_location=$(az group show --name "$RESOURCE_GROUP" --query location -o tsv)
        log_info "  Location: $rg_location"
    else
        log_warning "Creating resource group..."
        az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
        log_success "✓ Resource group created successfully"
    fi
}

# ============================================================================
# DEPLOYMENT VALIDATION
# ============================================================================

validate_deployment_template() {
    log_header "Template Validation"
    
    log_info "Validating Bicep template..."
    
    if az deployment group validate \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$BICEP_TEMPLATE" \
        --parameters "@$PARAMETERS_FILE" \
        --output none 2>&1 | tee -a "$LOG_FILE"; then
        log_success "✓ Template validation succeeded"
        return 0
    else
        log_error "✗ Template validation failed"
        return 1
    fi
}

# ============================================================================
# INFRASTRUCTURE DEPLOYMENT
# ============================================================================

deploy_infrastructure() {
    log_header "Infrastructure Deployment"
    
    log_info "Starting deployment: $DEPLOYMENT_NAME"
    log_info "  Resource Group: $RESOURCE_GROUP"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Location: $LOCATION"
    log_info "  Template: $BICEP_TEMPLATE"
    log_info "  Parameters: $PARAMETERS_FILE"
    
    log_info "Deploying infrastructure using Azure CLI..."
    
    if az deployment group create \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$BICEP_TEMPLATE" \
        --parameters "@$PARAMETERS_FILE" \
        --output json > /tmp/deployment-output.json 2>&1; then
        
        log_success "✓ Infrastructure deployment succeeded"
        return 0
    else
        log_error "✗ Infrastructure deployment failed"
        cat /tmp/deployment-output.json | tee -a "$LOG_FILE"
        return 1
    fi
}

# ============================================================================
# DEPLOYMENT STATUS VERIFICATION (BI-DIRECTIONAL)
# ============================================================================

get_deployment_status() {
    log_header "Deployment Status Verification"
    
    log_info "Retrieving deployment status from Azure..."
    
    # Get deployment details
    local deployment_json=$(az deployment group show \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --output json)
    
    local provisioning_state=$(echo "$deployment_json" | jq -r '.properties.provisioningState')
    local timestamp=$(echo "$deployment_json" | jq -r '.properties.timestamp')
    local duration=$(echo "$deployment_json" | jq -r '.properties.duration')
    
    log_info "Deployment Name: $DEPLOYMENT_NAME"
    log_info "Provisioning State: $provisioning_state"
    log_info "Timestamp: $timestamp"
    log_info "Duration: $duration"
    
    # Get resource list
    log_info ""
    log_info "Verifying deployed resources..."
    
    local resources=$(az resource list --resource-group "$RESOURCE_GROUP" --output json)
    local resource_count=$(echo "$resources" | jq 'length')
    
    log_info ""
    log_info "Deployed Resources ($resource_count):"
    
    # Group resources by type
    local resource_types=$(echo "$resources" | jq -r '.[].type' | sort | uniq)
    
    while IFS= read -r resource_type; do
        local type_count=$(echo "$resources" | jq -r --arg type "$resource_type" '[.[] | select(.type == $type)] | length')
        log_info "  $resource_type: $type_count resource(s)"
        
        # List individual resources
        echo "$resources" | jq -r --arg type "$resource_type" '.[] | select(.type == $type) | .name' | while read -r resource_name; do
            # Get resource provisioning state
            local resource_id=$(echo "$resources" | jq -r --arg name "$resource_name" --arg type "$resource_type" '.[] | select(.name == $name and .type == $type) | .id')
            local resource_state=$(az resource show --ids "$resource_id" --query 'properties.provisioningState' -o tsv 2>/dev/null || echo "N/A")
            
            if [[ "$resource_state" == "Succeeded" ]] || [[ "$resource_state" == "N/A" ]]; then
                log_success "    ✓ $resource_name [$resource_state]"
            else
                log_warning "    ✗ $resource_name [$resource_state]"
            fi
        done
    done <<< "$resource_types"
}

# ============================================================================
# POST-DEPLOYMENT VERIFICATION
# ============================================================================

test_deployed_resources() {
    log_header "Post-Deployment Verification"
    
    local all_tests_passed=true
    
    # Get deployment outputs
    local outputs=$(az deployment group show \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'properties.outputs' \
        --output json)
    
    # Test Storage Account
    local storage_name=$(echo "$outputs" | jq -r '.storageAccountName.value // empty')
    if [[ -n "$storage_name" ]]; then
        log_info "Testing Storage Account: $storage_name"
        
        if az storage account show --name "$storage_name" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
            local primary_endpoint=$(az storage account show --name "$storage_name" --resource-group "$RESOURCE_GROUP" --query 'primaryEndpoints.blob' -o tsv)
            log_success "  ✓ Storage Account accessible"
            log_info "    Primary Endpoint: $primary_endpoint"
        else
            log_error "  ✗ Storage Account test failed"
            all_tests_passed=false
        fi
    fi
    
    # Test Service Bus Namespace
    local sb_name=$(echo "$outputs" | jq -r '.serviceBusNamespaceName.value // empty')
    if [[ -n "$sb_name" ]]; then
        log_info "Testing Service Bus Namespace: $sb_name"
        
        if az servicebus namespace show --name "$sb_name" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
            local sb_endpoint=$(az servicebus namespace show --name "$sb_name" --resource-group "$RESOURCE_GROUP" --query 'serviceBusEndpoint' -o tsv)
            log_success "  ✓ Service Bus Namespace accessible"
            log_info "    Service Bus Endpoint: $sb_endpoint"
            
            # List queues
            local queues=$(az servicebus queue list --namespace-name "$sb_name" --resource-group "$RESOURCE_GROUP" --query '[].name' -o tsv)
            local queue_count=$(echo "$queues" | wc -l)
            log_info "    Queues: $queue_count"
            echo "$queues" | while read -r queue_name; do
                log_info "      - $queue_name"
            done
        else
            log_error "  ✗ Service Bus test failed"
            all_tests_passed=false
        fi
    fi
    
    # Test Key Vault
    local kv_name=$(echo "$outputs" | jq -r '.keyVaultName.value // empty')
    if [[ -n "$kv_name" ]]; then
        log_info "Testing Key Vault: $kv_name"
        
        if az keyvault show --name "$kv_name" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
            local vault_uri=$(az keyvault show --name "$kv_name" --resource-group "$RESOURCE_GROUP" --query 'properties.vaultUri' -o tsv)
            log_success "  ✓ Key Vault accessible"
            log_info "    Vault URI: $vault_uri"
        else
            log_error "  ✗ Key Vault test failed"
            all_tests_passed=false
        fi
    fi
    
    # Test Function Apps
    local func_name=$(echo "$outputs" | jq -r '.functionAppName.value // empty')
    if [[ -n "$func_name" ]]; then
        log_info "Testing Function App: $func_name"
        
        if az functionapp show --name "$func_name" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
            local func_state=$(az functionapp show --name "$func_name" --resource-group "$RESOURCE_GROUP" --query 'state' -o tsv)
            local func_url=$(az functionapp show --name "$func_name" --resource-group "$RESOURCE_GROUP" --query 'defaultHostName' -o tsv)
            log_success "  ✓ Function App accessible"
            log_info "    State: $func_state"
            log_info "    URL: https://$func_url"
        else
            log_error "  ✗ Function App test failed"
            all_tests_passed=false
        fi
    fi
    
    # Test Application Insights
    local ai_name=$(echo "$outputs" | jq -r '.appInsightsName.value // empty')
    if [[ -n "$ai_name" ]]; then
        log_info "Testing Application Insights: $ai_name"
        
        if az monitor app-insights component show --app "$ai_name" --resource-group "$RESOURCE_GROUP" --output none 2>/dev/null; then
            local instrumentation_key=$(az monitor app-insights component show --app "$ai_name" --resource-group "$RESOURCE_GROUP" --query 'instrumentationKey' -o tsv)
            log_success "  ✓ Application Insights accessible"
            log_info "    Instrumentation Key: ${instrumentation_key:0:8}..."
        else
            log_error "  ✗ Application Insights test failed"
            all_tests_passed=false
        fi
    fi
    
    if [[ "$all_tests_passed" == true ]]; then
        return 0
    else
        return 1
    fi
}

# ============================================================================
# FUNCTION APP CODE DEPLOYMENT
# ============================================================================

deploy_function_app_code() {
    log_header "Function App Code Deployment"
    
    if [[ "$DEPLOY_CODE" == false ]]; then
        log_warning "Code deployment skipped (use -c to enable)"
        return
    fi
    
    # Get Function App name from outputs
    local outputs=$(az deployment group show \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'properties.outputs' \
        --output json)
    
    local func_name=$(echo "$outputs" | jq -r '.functionAppName.value // empty')
    
    if [[ -z "$func_name" ]]; then
        log_error "Function App name not found in deployment outputs"
        return 1
    fi
    
    log_info "Deploying code to Function App: $func_name"
    
    # Create deployment package
    local deployment_package="/tmp/aos-deployment.zip"
    log_info "Creating deployment package..."
    
    # Remove old package if exists
    rm -f "$deployment_package"
    
    # Create zip package
    cd "$REPO_ROOT"
    zip -r "$deployment_package" \
        function_app.py \
        host.json \
        requirements.txt \
        src \
        azure_functions \
        config \
        -x "*.pyc" "*.git*" "*__pycache__*" "*.pytest_cache*" 2>&1 | tee -a "$LOG_FILE"
    
    log_success "✓ Deployment package created: $deployment_package"
    
    # Deploy to Azure
    log_info "Uploading package to Azure..."
    
    if az functionapp deployment source config-zip \
        --resource-group "$RESOURCE_GROUP" \
        --name "$func_name" \
        --src "$deployment_package" \
        --build-remote true \
        --output none 2>&1 | tee -a "$LOG_FILE"; then
        
        log_success "✓ Code deployment completed successfully"
    else
        log_error "✗ Code deployment failed"
        return 1
    fi
    
    # Clean up
    rm -f "$deployment_package"
}

# ============================================================================
# OUTPUT DEPLOYMENT SUMMARY
# ============================================================================

write_deployment_summary() {
    log_header "Deployment Summary"
    
    # Get deployment outputs
    local outputs=$(az deployment group show \
        --name "$DEPLOYMENT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query 'properties.outputs' \
        --output json 2>/dev/null)
    
    if [[ -z "$outputs" ]] || [[ "$outputs" == "null" ]]; then
        log_warning "No outputs available"
        return
    fi
    
    log_info "Deployment Outputs:"
    echo "" | tee -a "$LOG_FILE"
    
    # Storage Account
    local storage_name=$(echo "$outputs" | jq -r '.storageAccountName.value // empty')
    if [[ -n "$storage_name" ]]; then
        log_success "Storage Account:"
        log_info "  Name: $storage_name"
    fi
    
    # Service Bus
    local sb_name=$(echo "$outputs" | jq -r '.serviceBusNamespaceName.value // empty')
    if [[ -n "$sb_name" ]]; then
        echo "" | tee -a "$LOG_FILE"
        log_success "Service Bus:"
        log_info "  Namespace: $sb_name"
    fi
    
    # Key Vault
    local kv_name=$(echo "$outputs" | jq -r '.keyVaultName.value // empty')
    local kv_uri=$(echo "$outputs" | jq -r '.keyVaultUri.value // empty')
    if [[ -n "$kv_name" ]]; then
        echo "" | tee -a "$LOG_FILE"
        log_success "Key Vault:"
        log_info "  Name: $kv_name"
        log_info "  URI: $kv_uri"
    fi
    
    # Function Apps
    local func_name=$(echo "$outputs" | jq -r '.functionAppName.value // empty')
    local func_url=$(echo "$outputs" | jq -r '.functionAppUrl.value // empty')
    if [[ -n "$func_name" ]]; then
        echo "" | tee -a "$LOG_FILE"
        log_success "Function Apps:"
        log_info "  Main App: $func_name"
        log_info "    URL: $func_url"
        
        local mcp_name=$(echo "$outputs" | jq -r '.mcpServerFunctionAppName.value // empty')
        local mcp_url=$(echo "$outputs" | jq -r '.mcpServerFunctionAppUrl.value // empty')
        if [[ -n "$mcp_name" ]]; then
            log_info "  MCP Server App: $mcp_name"
            log_info "    URL: $mcp_url"
        fi
        
        local realm_name=$(echo "$outputs" | jq -r '.realmFunctionAppName.value // empty')
        local realm_url=$(echo "$outputs" | jq -r '.realmFunctionAppUrl.value // empty')
        if [[ -n "$realm_name" ]]; then
            log_info "  Realm App: $realm_name"
            log_info "    URL: $realm_url"
        fi
    fi
    
    # Application Insights
    local ai_name=$(echo "$outputs" | jq -r '.appInsightsName.value // empty')
    if [[ -n "$ai_name" ]]; then
        echo "" | tee -a "$LOG_FILE"
        log_success "Application Insights:"
        log_info "  Name: $ai_name"
    fi
    
    # Azure ML
    local ml_name=$(echo "$outputs" | jq -r '.azureMLWorkspaceName.value // empty')
    if [[ -n "$ml_name" ]]; then
        echo "" | tee -a "$LOG_FILE"
        log_success "Azure ML Workspace:"
        log_info "  Name: $ml_name"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    log_info "Log file: $LOG_FILE"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    local start_time=$(date +%s)
    
    log_header "Agent Operating System - Azure Deployment"
    log_info "Started: $(date)"
    log_info "Environment: $ENVIRONMENT"
    log_info "Resource Group: $RESOURCE_GROUP"
    log_info "Location: $LOCATION"
    echo "" | tee -a "$LOG_FILE"
    
    # Step 1: Prerequisites
    if ! check_prerequisites; then
        log_error "✗ Prerequisites check failed. Please resolve issues and try again."
        exit 1
    fi
    
    # Step 2: Azure Authentication
    initialize_azure_connection
    
    # Step 3: Resource Group
    initialize_resource_group
    
    # Step 4: Pre-deployment validation
    if [[ "$SKIP_PRE_CHECK" == false ]]; then
        if ! validate_deployment_template; then
            log_error "✗ Template validation failed. Please fix errors and try again."
            exit 1
        fi
    else
        log_warning "Skipping pre-deployment validation (as requested)"
    fi
    
    # Step 5: Deploy Infrastructure
    if ! deploy_infrastructure; then
        log_error "✗ Infrastructure deployment failed"
        exit 1
    fi
    
    # Step 6: Verify Deployment Status (Bi-directional check)
    get_deployment_status
    
    # Step 7: Post-deployment verification
    if [[ "$SKIP_POST_CHECK" == false ]]; then
        if ! test_deployed_resources; then
            log_warning "⚠ Some post-deployment tests failed. Please review."
        fi
    else
        log_warning "Skipping post-deployment verification (as requested)"
    fi
    
    # Step 8: Deploy Function App code (optional)
    if [[ "$DEPLOY_CODE" == true ]]; then
        deploy_function_app_code
    fi
    
    # Step 9: Summary
    write_deployment_summary
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local duration_formatted=$(printf '%02d:%02d:%02d' $((duration/3600)) $((duration%3600/60)) $((duration%60)))
    
    log_header "Deployment Complete"
    log_success "✓ Deployment completed successfully!"
    log_info "Duration: $duration_formatted"
    log_info "End Time: $(date)"
    
    exit 0
}

# Parse command line arguments
parse_arguments "$@"

# Execute main function
main
