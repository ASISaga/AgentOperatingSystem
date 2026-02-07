"""Shared test configuration and fixtures for AOS tests."""

import sys
import os

# Ensure src is on the path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
