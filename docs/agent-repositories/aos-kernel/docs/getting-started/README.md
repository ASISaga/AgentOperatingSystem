# Getting Started with AOS Kernel

## Prerequisites

- Python 3.10+
- Azure credentials (for Azure service backends)

## Installation

```bash
pip install aos-kernel
```

## First Steps

```python
from AgentOperatingSystem import AgentOperatingSystem

aos = AgentOperatingSystem()
await aos.initialize()
await aos.start()
```

See the [examples/](../../examples/) directory for more usage patterns.
