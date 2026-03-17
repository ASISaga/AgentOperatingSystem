from enum import Enum

class State(Enum):
    """States of the autonomous boardroom"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DELIBERATING = "deliberating"
    EXECUTING = "executing"
    SUSPENDED = "suspended"
    MAINTENANCE = "maintenance"
