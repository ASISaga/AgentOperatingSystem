"""
Basic usage example for purpose-driven-agent.

Demonstrates:
- Creating a GenericPurposeDrivenAgent
- Initialising and starting the agent
- Subscribing to events
- Handling events
- Adding and tracking goals
- Purpose-driven decision making
- Querying status and state
- Graceful shutdown
"""

from __future__ import annotations

import asyncio
import logging

from purpose_driven_agent import GenericPurposeDrivenAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def demo_basic_agent() -> None:
    """Demonstrate basic GenericPurposeDrivenAgent usage."""
    print("\n=== Basic Agent Demo ===\n")

    agent = GenericPurposeDrivenAgent(
        agent_id="demo-assistant",
        purpose="Assist users with information retrieval and task coordination",
        purpose_scope="Knowledge queries and workflow orchestration",
        success_criteria=[
            "Respond to all queries within 2 seconds",
            "Maintain >90% user satisfaction",
            "Process >1000 events per day",
        ],
        adapter_name="general",
    )

    print(f"Agent created: {agent.agent_id}")
    print(f"Purpose:       {agent.purpose}")
    print(f"Adapter:       {agent.adapter_name}")
    print(f"Personas:      {agent.get_agent_type()}")

    # ------------------------------------------------------------------
    # Initialise and start
    # ------------------------------------------------------------------

    print("\n--- Initialising ---")
    ok = await agent.initialize()
    print(f"Initialised:   {ok}")

    print("\n--- Starting perpetual operation ---")
    ok = await agent.start()
    print(f"Running:       {ok}")

    # ------------------------------------------------------------------
    # Event subscription
    # ------------------------------------------------------------------

    print("\n--- Subscribing to events ---")

    async def on_user_query(data: dict) -> dict:
        print(f"  Handler received query: {data.get('query', '<no query>')}")
        return {"response": f"Processed: {data.get('query', '')}"}

    await agent.subscribe_to_event("user_query", on_user_query)

    # ------------------------------------------------------------------
    # Process events
    # ------------------------------------------------------------------

    print("\n--- Processing events ---")

    events = [
        {"type": "user_query", "data": {"query": "What is AOS?"}},
        {"type": "user_query", "data": {"query": "How do perpetual agents work?"}},
        {"type": "system_heartbeat", "data": {}},
    ]

    for event in events:
        result = await agent.handle_event(event)
        print(f"  Event '{event['type']}' → status={result['status']}")

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------

    print("\n--- Goal tracking ---")

    goal_id = await agent.add_goal(
        "Deploy to production",
        success_criteria=["All tests pass", "Deployment succeeds"],
    )
    print(f"  Added goal: {goal_id}")

    await agent.update_goal_progress(goal_id, 0.5, notes="Tests passing, deploying…")
    print(f"  Updated goal progress to 50%")

    await agent.update_goal_progress(goal_id, 1.0, notes="Deployment complete")
    print(f"  Goal completed!")

    # ------------------------------------------------------------------
    # Purpose-driven decision making
    # ------------------------------------------------------------------

    print("\n--- Purpose-driven decision ---")

    decision = await agent.make_purpose_driven_decision({
        "options": [
            {"type": "expand_features", "description": "Add new features"},
            {"type": "fix_bugs", "description": "Fix existing bugs"},
            {"type": "improve_docs", "description": "Improve documentation"},
        ]
    })
    print(f"  Decision ID:     {decision['decision_id']}")
    print(f"  Selected option: {decision['selected_option']}")
    print(f"  Alignment score: {decision['alignment_score']:.2f}")

    # ------------------------------------------------------------------
    # Status and state queries
    # ------------------------------------------------------------------

    print("\n--- Status ---")
    status = await agent.get_purpose_status()
    print(f"  Events processed:  {status['total_events_processed']}")
    print(f"  Active goals:      {status['active_goals']}")
    print(f"  Completed goals:   {status['completed_goals']}")
    print(f"  Purpose aligned:   {status['metrics']['purpose_aligned_actions']}")

    print("\n--- State ---")
    state = await agent.get_state()
    print(f"  Is running:         {state['is_running']}")
    print(f"  Sleep mode:         {state['sleep_mode']}")
    print(f"  Wake count:         {state['wake_count']}")
    print(f"  MCP context saved:  {state['mcp_context_preserved']}")

    # ------------------------------------------------------------------
    # Graceful shutdown
    # ------------------------------------------------------------------

    print("\n--- Stopping ---")
    ok = await agent.stop()
    print(f"Stopped gracefully: {ok}")

    print("\n=== Demo complete ===\n")


async def demo_custom_subclass() -> None:
    """Demonstrate creating a custom PurposeDrivenAgent subclass."""
    from purpose_driven_agent import PurposeDrivenAgent
    from typing import List

    class ResearchAgent(PurposeDrivenAgent):
        """Custom research-focused agent."""

        def get_agent_type(self) -> List[str]:
            return ["research"]

        async def analyse(self, topic: str) -> dict:
            """Perform purpose-aligned analysis on a topic."""
            alignment = await self.evaluate_purpose_alignment(
                {"type": "analyse", "topic": topic}
            )
            return {
                "topic": topic,
                "purpose": self.purpose,
                "alignment_score": alignment["alignment_score"],
                "summary": f"Analysis of '{topic}' aligns with research purpose",
            }

    print("\n=== Custom Subclass Demo ===\n")

    researcher = ResearchAgent(
        agent_id="research-agent-01",
        purpose="Conduct rigorous scientific research and synthesise findings",
        adapter_name="research",
    )
    await researcher.initialize()

    result = await researcher.analyse("Perpetual AI Agents")
    print(f"Topic:      {result['topic']}")
    print(f"Alignment:  {result['alignment_score']:.2f}")
    print(f"Summary:    {result['summary']}")

    await researcher.stop()
    print("\n=== Custom Subclass Demo complete ===\n")


async def main() -> None:
    await demo_basic_agent()
    await demo_custom_subclass()


if __name__ == "__main__":
    asyncio.run(main())
