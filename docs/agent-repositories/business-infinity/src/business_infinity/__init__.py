"""BusinessInfinity — lean Azure Functions client application.

BusinessInfinity demonstrates how a client application uses the Agent Operating
System as an infrastructure service.  It contains only business logic — agent
lifecycle, orchestration, messaging, and storage are handled by AOS.

Usage::

    # Browse the C-suite agent catalog
    agents = await client.list_agents()

    # Run a strategic review orchestration
    result = await client.run_orchestration(
        agent_ids=["ceo", "cfo", "cmo", "coo", "cto"],
        task={"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
    )
"""

__version__ = "1.0.0"
