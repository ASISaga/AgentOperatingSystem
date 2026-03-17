# Installation Guide

## Prerequisites

- Python 3.8+
- Microsoft Azure subscription
- Azure CLI (for deployment)

## Installation Options

### Install from GitHub

```bash
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git
```

### Install with All Optional Dependencies

```bash
pip install "AgentOperatingSystem[full]"
```

### Install Specific Service Groups

```bash
# Azure services
pip install "AgentOperatingSystem[azure]"

# ML capabilities
pip install "AgentOperatingSystem[ml]"

# MCP integration
pip install "AgentOperatingSystem[mcp]"
```

## Verify Installation

```python
import AgentOperatingSystem
print(AgentOperatingSystem.__version__)
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Get started quickly
- [Configuration Guide](../configuration.md) - Configure the system
- [Deployment Guide](deployment.md) - Deploy to production

## See Also

- [Quick Start](quickstart.md) - Quick start example
- [Configuration](../configuration.md) - System configuration
- [Development Guide](../development.md) - Development documentation
