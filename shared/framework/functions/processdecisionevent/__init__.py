"""
Process Decision Event - Updated to use new trigger structure

This module now imports from the consolidated triggers module.
The actual trigger implementation is in triggers/service_bus_triggers.py
"""

import logging
from triggers.service_bus_triggers import register_service_bus_triggers

def main(msg):
    """
    Legacy main function for backward compatibility.
    The actual trigger is now registered in triggers/service_bus_triggers.py
    """
    logging.info("processdecisionevent.main() called - this function is deprecated.")
    logging.info("Trigger functionality has been moved to triggers/service_bus_triggers.py")
    logging.info("Please use the new trigger registration system.")
    # We could call the new trigger function here if needed for compatibility
    # But it's better to use the new system directly
