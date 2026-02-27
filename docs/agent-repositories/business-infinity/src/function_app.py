"""BusinessInfinity Azure Functions entry point.

The SDK handles all Azure Functions scaffolding.  This file simply imports
the ``AOSApp`` with registered workflows and generates the Functions triggers.
"""

from business_infinity.workflows import app  # noqa: F401

functions = app.get_functions()
