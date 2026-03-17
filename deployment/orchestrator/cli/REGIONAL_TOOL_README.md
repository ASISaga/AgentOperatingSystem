# Regional Capability CLI Tool

## Overview

The Regional Capability CLI Tool provides command-line interface for validating Azure region capabilities, recommending optimal regions, and generating deployment summaries for the Agent Operating System (AOS).

## Features

- ✅ **Validate** regions for required services
- ✅ **Recommend** optimal regions based on requirements
- ✅ **Check** capabilities of specific regions
- ✅ **Generate summaries** for deployment planning
- ✅ **JSON output** for automation
- ✅ **Geographic preferences** (Americas, Europe, Asia)
- ✅ **Tier-based ranking** (Tier 1, 2, 3)

## Installation

The tool is included in the AOS deployment orchestrator:

```bash
cd deployment/orchestrator/cli
chmod +x regional_tool.py
```

No additional dependencies required (uses standard Python libraries).

## Commands

### 1. validate - Validate Region Compatibility

Check if a region supports required services.

**Usage:**
```bash
python3 regional_tool.py validate <region> <service1> [service2 ...]
```

**Options:**
- `--json` - Output as JSON for automation

**Examples:**
```bash
# Check if eastus supports storage and Azure ML
python3 regional_tool.py validate eastus storage azureml

# Check with JSON output
python3 regional_tool.py validate eastasia storage azureml functions-premium --json
```

**Output (Success):**
```
Region: eastus
Valid: ✅ Yes

✅ No warnings - region fully supports all requested services
```

**Output (With Warnings):**
```
Region: eastasia
Valid: ❌ No

Warnings:
  • Region 'eastasia' does not support: azureml
  • → Azure ML deployment will be automatically disabled
  • Region 'eastasia' is Tier 3 (basic coverage) - consider Tier 1 region for production
```

**Exit Codes:**
- `0` - Region is valid (all services supported)
- `1` - Region has warnings (some services unavailable)

---

### 2. recommend - Get Region Recommendations

Get recommended regions for required services, optionally filtered by geography.

**Usage:**
```bash
python3 regional_tool.py recommend <service1> [service2 ...] [OPTIONS]
```

**Options:**
- `--geography <americas|europe|asia>` - Prefer regions in specific geography
- `--limit <N>` - Number of recommendations (default: 5)
- `--json` - Output as JSON

**Examples:**
```bash
# Get top 5 recommendations for storage and Azure ML
python3 regional_tool.py recommend storage azureml

# Prefer Americas, limit to 3
python3 regional_tool.py recommend storage azureml functions-premium --geography americas --limit 3

# JSON output
python3 regional_tool.py recommend storage azureml --json
```

**Output:**
```
Services Required: azureml, storage

Top 5 Recommended Regions:

1. westus2              🏆 tier1      100% compatible
2. japaneast            🏆 tier1      100% compatible
3. eastus               🏆 tier1      100% compatible
4. northeurope          🏆 tier1      100% compatible
5. southeastasia        🏆 tier1      100% compatible
```

**Output (JSON):**
```json
{
  "services": ["storage", "azureml"],
  "geography": "americas",
  "recommendations": [
    {
      "region": "eastus",
      "compatibility_score": 1.0,
      "tier": "tier1"
    },
    {
      "region": "westus2",
      "compatibility_score": 1.0,
      "tier": "tier1"
    }
  ]
}
```

---

### 3. check - Check Region Capabilities

View complete capabilities of a specific region.

**Usage:**
```bash
python3 regional_tool.py check <region> [--json]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
# Check capabilities of eastus
python3 regional_tool.py check eastus

# JSON output
python3 regional_tool.py check eastus --json
```

**Output:**
```
Region: eastus
Tier: Tier 1 (Full Capability)

Available Services (12):
  ✅ acr
  ✅ appinsights
  ✅ azureml
  ✅ functions_consumption
  ✅ functions_premium
  ✅ keyvault
  ✅ loganalytics
  ✅ managedidentity
  ✅ servicebus_basic
  ✅ servicebus_premium
  ✅ servicebus_standard
  ✅ storage
```

---

### 4. summary - Generate Deployment Summary

Generate a deployment summary showing compatibility analysis and recommendations.

**Usage:**
```bash
python3 regional_tool.py summary <region> <service1> [service2 ...] [--json]
```

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
# Generate summary for eastasia with Azure ML
python3 regional_tool.py summary eastasia storage azureml functions-premium

# JSON output
python3 regional_tool.py summary eastasia storage azureml --json
```

**Output:**
```
Deployment Summary for eastasia

Region Tier: tier3
Compatibility Score: 66%
Valid for Deployment: ❌ No

Supported Services (2):
  ✅ storage
  ✅ functions_premium

Unsupported Services (1):
  ❌ azureml

Warnings:
  ⚠️  Region 'eastasia' does not support: azureml
  ⚠️  → Azure ML deployment will be automatically disabled
  ⚠️  Region 'eastasia' is Tier 3 (basic coverage) - consider Tier 1 region for production

Recommended Alternatives:
  1. southeastasia (tier1, 100% compatible)
  2. japaneast (tier1, 100% compatible)
  3. australiaeast (tier1, 100% compatible)
```

---

## Supported Services

| Service Name | Description | Availability |
|--------------|-------------|--------------|
| `storage` | Azure Storage (Blob, Table, Queue) | All regions |
| `keyvault` | Azure Key Vault | All regions |
| `identity` | Managed Identity | All regions |
| `functions` | Azure Functions (Consumption Y1) | All regions |
| `functions-premium` | Azure Functions (Premium EP1/2/3) | Most regions |
| `servicebus` | Service Bus (Basic/Standard) | All regions |
| `servicebus-premium` | Service Bus Premium | Most regions |
| `appinsights` | Application Insights | Most regions |
| `loganalytics` | Log Analytics Workspace | Most regions |
| `azureml` | Azure Machine Learning | Limited regions (19) |
| `acr` | Azure Container Registry | Most regions |

---

## Region Tiers

### Tier 1 - Full Capability (8 regions)
**All services available, recommended for production**

**Americas:**
- `eastus` - East US ⭐ Recommended
- `eastus2` - East US 2
- `westus2` - West US 2 ⭐ Recommended

**Europe:**
- `westeurope` - West Europe ⭐ Recommended
- `northeurope` - North Europe ⭐ Recommended

**Asia Pacific:**
- `southeastasia` - Southeast Asia ⭐ Recommended
- `australiaeast` - Australia East
- `japaneast` - Japan East

### Tier 2 - Good Coverage (7 regions)
**Most services available, suitable for production**

**Americas:**
- `westus3` - West US 3
- `canadacentral` - Canada Central

**Europe:**
- `uksouth` - UK South
- `francecentral` - France Central
- `swedencentral` - Sweden Central

**Asia Pacific:**
- `koreacentral` - Korea Central
- `centralindia` - Central India

### Tier 3 - Basic Coverage (18 regions)
**Core services only, suitable for dev/test**

Includes: brazilsouth, eastasia, southafricanorth, and others

---

## Integration with GitHub Workflow

The infrastructure-deploy.yml workflow automatically runs regional validation before deployment:

```yaml
- name: Regional Capability Validation
  run: |
    python3 deployment/orchestrator/cli/regional_tool.py validate $LOCATION $SERVICES
    
    # If validation fails, show recommendations
    if [[ $? -ne 0 ]]; then
      python3 deployment/orchestrator/cli/regional_tool.py recommend $SERVICES --geography americas --limit 3
    fi
```

The workflow automatically:
1. Detects required services based on environment (dev/staging/prod)
2. Validates the target region
3. Shows warnings if services are unavailable
4. Recommends alternative regions
5. Generates deployment summary

---

## Use Cases

### 1. Pre-Deployment Validation

Before deploying, check if your region supports required services:

```bash
# Production deployment needs premium SKUs and Azure ML
python3 regional_tool.py validate eastus storage keyvault functions-premium servicebus-premium azureml

# If validation fails, get recommendations
python3 regional_tool.py recommend storage functions-premium servicebus-premium azureml --geography americas
```

### 2. Region Selection

Find the best region for your requirements:

```bash
# Need Azure ML and premium functions in Europe
python3 regional_tool.py recommend azureml functions-premium --geography europe --limit 5
```

### 3. Compliance/Data Residency

Check if a specific region (required for compliance) supports your needs:

```bash
# Must use brazilsouth for data residency
python3 regional_tool.py summary brazilsouth storage azureml functions-premium

# If not supported, get alternatives in same geography
python3 regional_tool.py recommend storage azureml functions-premium --geography americas
```

### 4. Cost Optimization

Compare regions to find most cost-effective option:

```bash
# Dev environment - only need basic services
python3 regional_tool.py recommend storage functions servicebus --limit 10

# Choose from Tier 2/3 regions for lower costs
```

### 5. Automation/CI/CD

Use JSON output in scripts:

```bash
#!/bin/bash

# Validate region and get JSON result
RESULT=$(python3 regional_tool.py validate eastus storage azureml --json)

# Parse JSON
IS_VALID=$(echo "$RESULT" | jq -r '.is_valid')

if [[ "$IS_VALID" == "false" ]]; then
  echo "Region validation failed, finding alternative..."
  python3 regional_tool.py recommend storage azureml --json | jq -r '.recommendations[0].region'
fi
```

---

## Best Practices

### 1. **Always Validate Before Deployment**
```bash
python3 regional_tool.py validate $REGION $SERVICES
```

### 2. **Use Tier 1 Regions for Production**
```bash
python3 regional_tool.py recommend $SERVICES | grep tier1
```

### 3. **Respect Geographic Constraints**
```bash
python3 regional_tool.py recommend $SERVICES --geography europe
```

### 4. **Check Summaries for Planning**
```bash
python3 regional_tool.py summary $REGION $SERVICES
```

### 5. **Use JSON for Automation**
```bash
python3 regional_tool.py validate $REGION $SERVICES --json | jq
```

---

## Troubleshooting

### Error: "Unknown service"

**Cause:** Invalid service name provided

**Solution:** Use valid service names (see Supported Services table)

```bash
# Wrong
python3 regional_tool.py validate eastus azure-ml

# Correct
python3 regional_tool.py validate eastus azureml
```

### Warning: "Region is Tier 3"

**Cause:** Region has limited service availability

**Solution:** Consider Tier 1 region for production, or accept limitations

```bash
# Get Tier 1 alternatives
python3 regional_tool.py recommend $SERVICES | grep tier1
```

### No Recommendations Returned

**Cause:** No regions support all requested services

**Solution:** Review service requirements, some may not be available anywhere

```bash
# Check each service individually
for service in storage azureml functions-premium; do
  echo "Checking $service..."
  python3 regional_tool.py recommend $service --limit 1
done
```

---

## Advanced Usage

### Scripting Example

```bash
#!/bin/bash

# Function to select best region
select_best_region() {
  local services="$@"
  local geography="${PREFERRED_GEOGRAPHY:-americas}"
  
  # Get recommendations
  local recommendations=$(python3 regional_tool.py recommend $services --geography $geography --json)
  
  # Extract best region
  local best_region=$(echo "$recommendations" | jq -r '.recommendations[0].region')
  
  # Validate
  if python3 regional_tool.py validate $best_region $services --json | jq -e '.is_valid' > /dev/null; then
    echo "$best_region"
    return 0
  else
    echo "Error: No suitable region found" >&2
    return 1
  fi
}

# Use it
REGION=$(select_best_region storage azureml functions-premium)
echo "Selected region: $REGION"
```

### Python API Usage

```python
from validators.regional_validator import RegionalValidator, ServiceType

validator = RegionalValidator()

# Define required services
services = {
    ServiceType.STORAGE,
    ServiceType.AZURE_ML,
    ServiceType.FUNCTIONS_PREMIUM
}

# Validate region
is_valid, warnings = validator.validate_region('eastus', services)

if not is_valid:
    # Get recommendations
    recommendations = validator.recommend_regions(services, 'americas', limit=3)
    print(f"Recommended: {recommendations[0][0]}")

# Generate summary
summary = validator.generate_deployment_summary('eastus', services)
print(f"Compatibility: {summary['compatibility_score']*100}%")
```

---

## Related Documentation

- [REGIONAL_REQUIREMENTS.md](../../REGIONAL_REQUIREMENTS.md) - Detailed service availability
- [REGIONAL_VALIDATION_FLOW.md](../../docs/REGIONAL_VALIDATION_FLOW.md) - Validation flow diagrams
- [DEPLOYMENT_PLAN.md](../../../docs/development/DEPLOYMENT_PLAN.md) - Complete deployment guide
- [infrastructure-deploy.yml](../../../.github/workflows/infrastructure-deploy.yml) - GitHub workflow integration

---

## Support

For questions or issues:
1. Check this documentation
2. Review regional requirements documentation
3. Open an issue: https://github.com/ASISaga/AgentOperatingSystem/issues

---

**Version:** 1.0  
**Last Updated:** February 19, 2026
