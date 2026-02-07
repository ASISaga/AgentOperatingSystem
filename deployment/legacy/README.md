# Legacy Deployment Scripts

This directory contains legacy deployment scripts that have been **superseded by the Python orchestrator** (`deploy.py`).

## Archived Files

### deploy-aos.sh
- **Purpose**: Bash deployment script for Linux/macOS
- **Status**: ⛔ Deprecated - Use `python3 deploy.py` instead
- **Reason**: Replaced by production-grade Python orchestrator with:
  - Mandatory linting and validation
  - What-if analysis with destructive change detection
  - Post-deployment health checks
  - Smart retry strategies
  - Complete audit trail

### Deploy-AOS.ps1
- **Purpose**: PowerShell deployment script for Windows
- **Status**: ⛔ Deprecated - Use `python3 deploy.py` instead
- **Reason**: Same as above

## Migration to Python Orchestrator

Instead of using these legacy scripts, use the Python orchestrator:

```bash
# Development deployment
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam"

# Production deployment
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus2" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam"
```

See [ORCHESTRATOR_USER_GUIDE.md](../ORCHESTRATOR_USER_GUIDE.md) for complete documentation.

## Why These Scripts Were Deprecated

The legacy scripts lacked:
- ❌ Static analysis and linting gates
- ❌ What-if planning and risk assessment
- ❌ Post-deployment health verification
- ❌ Intelligent failure classification and retry
- ❌ Structured audit logging
- ❌ Deployment state management

The Python orchestrator provides all of these features in a production-grade framework.

---

**Note**: These files are kept for historical reference only. For all new deployments, use the Python orchestrator.
