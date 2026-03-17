#!/usr/bin/env python3
"""
Bicep Deployment Orchestrator Entry Point

This script provides a convenient entry point for running deployments.
"""

import sys
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.cli.deploy import main

if __name__ == "__main__":
    main()
