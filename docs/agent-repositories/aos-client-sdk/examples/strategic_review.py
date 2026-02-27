"""Example: BusinessInfinity-style C-suite orchestration via AOS.

This example shows how a lean client application uses the AOS Client SDK
to browse agents, compose orchestrations, and retrieve results — without
any agent or infrastructure code.

Prerequisites:
    pip install aos-client-sdk

    AOS must be running:
    - aos-function-app at AOS_ENDPOINT (default: http://localhost:7071)
    - aos-realm-of-agents at REALM_ENDPOINT (default: same as AOS_ENDPOINT)
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

        # ── Step 3: Run a strategic review orchestration ─────────────
        print("\n=== Running Strategic Review ===")
        result = await client.run_orchestration(
            agent_ids=c_suite_ids,
            task={
                "type": "strategic_review",
                "data": {
                    "quarter": "Q1-2026",
                    "focus_areas": ["revenue", "growth", "efficiency"],
                },
            },
            workflow="collaborative",
        )
        print(f"Result: {result.summary}")
        print(f"Per-agent results: {result.results}")


if __name__ == "__main__":
    asyncio.run(main())
