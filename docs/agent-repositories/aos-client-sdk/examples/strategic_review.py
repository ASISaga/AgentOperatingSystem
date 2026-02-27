"""Example: BusinessInfinity-style C-suite orchestration via AOS.

This example shows how a lean client application uses the AOS Client SDK
to browse agents and start perpetual orchestrations — without
any agent or infrastructure code.

Prerequisites:
    pip install aos-client-sdk[azure]

    AOS must be running:
    - aos-function-app at AOS_ENDPOINT (default: http://localhost:7071)
    - aos-realm-of-agents at REALM_ENDPOINT (default: same as AOS_ENDPOINT)

Option A: Use AOSApp framework (recommended for Azure Functions)

    from aos_client import AOSApp, WorkflowRequest

    app = AOSApp(name="my-app")

    @app.workflow("strategic-review")
    async def strategic_review(request: WorkflowRequest):
        agents = await request.client.list_agents()
        c_suite = [a.agent_id for a in agents]
        return await request.client.start_orchestration(
            agent_ids=c_suite,
            purpose="strategic_review",
            context=request.body,
        )

Option B: Use AOSClient directly (for scripts and non-Functions apps)
"""

import asyncio
import os

from aos_client import AOSClient


async def main():
    aos_endpoint = os.environ.get("AOS_ENDPOINT", "http://localhost:7071")
    realm_endpoint = os.environ.get("REALM_ENDPOINT", aos_endpoint)

    async with AOSClient(endpoint=aos_endpoint, realm_endpoint=realm_endpoint) as client:
        # ── Step 1: Browse the agent catalog ─────────────────────────
        print("=== Agent Catalog ===")
        agents = await client.list_agents()
        for agent in agents:
            print(f"  {agent.agent_id}: {agent.purpose} ({agent.agent_type})")

        # ── Step 2: Select C-suite agents ────────────────────────────
        c_suite_ids = [a.agent_id for a in agents]
        print(f"\nSelected C-suite: {c_suite_ids}")

        # ── Step 3: Start a strategic review orchestration (perpetual) ──
        print("\n=== Starting Strategic Review ===")
        status = await client.start_orchestration(
            agent_ids=c_suite_ids,
            purpose="strategic_review",
            context={
                "quarter": "Q1-2026",
                "focus_areas": ["revenue", "growth", "efficiency"],
            },
        )
        print(f"Orchestration ID: {status.orchestration_id}")
        print(f"Status: {status.status}")  # "ACTIVE"


if __name__ == "__main__":
    asyncio.run(main())
