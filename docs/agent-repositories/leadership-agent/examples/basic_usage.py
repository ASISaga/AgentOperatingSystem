"""
Basic usage example for leadership-agent.

Demonstrates:
- Creating a LeadershipAgent
- Initialising and starting the agent
- Making decisions with different modes
- Handling events
- Tracking goal progress
- Decision provenance / history
- Graceful shutdown
"""

from __future__ import annotations

import asyncio
import logging

from leadership_agent import LeadershipAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def demo_leadership_agent() -> None:
    """Demonstrate LeadershipAgent decision-making capabilities."""
    print("\n=== Leadership Agent Demo ===\n")

    agent = LeadershipAgent(
        agent_id="ceo-001",
        name="CEO Agent",
        purpose=(
            "Leadership: Drive company growth through strategic decisions "
            "and organisational alignment"
        ),
        purpose_scope="Strategic planning, major decisions, cross-team coordination",
        adapter_name="leadership",
    )

    print(f"Agent:    {agent.agent_id} ({agent.name})")
    print(f"Role:     {agent.role}")
    print(f"Adapter:  {agent.adapter_name}")
    print(f"Personas: {agent.get_agent_type()}")

    # ------------------------------------------------------------------
    # Initialise and start
    # ------------------------------------------------------------------

    print("\n--- Initialising ---")
    ok = await agent.initialize()
    print(f"Initialised: {ok}")

    ok = await agent.start()
    print(f"Running:     {ok}")

    # ------------------------------------------------------------------
    # Event subscription
    # ------------------------------------------------------------------

    async def on_proposal_received(data: dict) -> dict:
        print(f"  Proposal received: {data.get('title', '<no title>')}")
        return {"acknowledged": True, "review_scheduled": True}

    await agent.subscribe_to_event("proposal", on_proposal_received)

    # ------------------------------------------------------------------
    # Making decisions
    # ------------------------------------------------------------------

    print("\n--- Autonomous decision ---")
    decision = await agent.make_decision(
        context={
            "proposal": "Expand to European market",
            "budget_required": 2_000_000,
            "expected_roi": "35% within 18 months",
            "risks": ["regulatory compliance", "currency exposure"],
        },
        mode="autonomous",
    )
    print(f"  Decision ID:   {decision['id']}")
    print(f"  Mode:          {decision['mode']}")
    print(f"  Outcome:       {decision['decision']}")

    print("\n--- Consensus decision (with stakeholders) ---")
    consensus_decision = await agent.make_decision(
        context={"topic": "Hire 50 engineers in Q3"},
        stakeholders=["cto-agent", "cfo-agent", "coo-agent"],
        mode="consensus",
    )
    print(f"  Decision ID:   {consensus_decision['id']}")
    print(f"  Stakeholders:  {consensus_decision['stakeholders']}")

    # ------------------------------------------------------------------
    # consult_stakeholders (shows NotImplementedError)
    # ------------------------------------------------------------------

    print("\n--- Stakeholder consultation (requires message bus) ---")
    try:
        await agent.consult_stakeholders(
            stakeholders=["cfo-agent"],
            topic="Budget approval",
            context={"amount": 500_000},
        )
    except NotImplementedError as exc:
        print(f"  Expected: {exc}")

    # ------------------------------------------------------------------
    # Goal tracking
    # ------------------------------------------------------------------

    print("\n--- Goals ---")
    goal_id = await agent.add_goal(
        "Launch EU product line",
        success_criteria=["Legal entity registered", "Website localised", "Launch event held"],
    )
    print(f"  Goal created: {goal_id}")
    await agent.update_goal_progress(goal_id, 0.3, "Legal entity registered")
    await agent.update_goal_progress(goal_id, 0.6, "Website localised")
    await agent.update_goal_progress(goal_id, 1.0, "Launch event completed!")
    print(f"  Goals achieved: {agent.purpose_metrics['goals_achieved']}")

    # ------------------------------------------------------------------
    # Decision history
    # ------------------------------------------------------------------

    print("\n--- Decision history ---")
    history = await agent.get_decision_history(limit=5)
    print(f"  Recent decisions: {len(history)}")
    for d in history:
        print(f"    [{d['mode']}] {d['id'][:8]}…")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    print("\n--- Status ---")
    status = await agent.get_purpose_status()
    print(f"  Decisions made:     {status['metrics']['decisions_made']}")
    print(f"  Goals completed:    {status['metrics']['goals_achieved']}")
    print(f"  Events processed:   {status['total_events_processed']}")

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    print("\n--- Stopping ---")
    ok = await agent.stop()
    print(f"Stopped gracefully: {ok}")

    print("\n=== Demo complete ===\n")


async def demo_custom_decision_logic() -> None:
    """Demonstrate overriding _evaluate_decision for domain logic."""
    from typing import Any, Dict, Optional, List

    class BudgetDecisionAgent(LeadershipAgent):
        """Leader that evaluates budget proposals."""

        async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
            amount = context.get("budget_required", 0)
            threshold = self.config.get("approval_threshold", 100_000)
            if amount <= threshold:
                return {"approved": True, "reason": f"Within threshold (${threshold:,})"}
            return {"approved": False, "reason": f"Exceeds threshold (${threshold:,})"}

    print("\n=== Custom Decision Logic Demo ===\n")

    agent = BudgetDecisionAgent(
        agent_id="budget-approver",
        config={"approval_threshold": 50_000},
    )
    await agent.initialize()

    for amount in [25_000, 75_000]:
        d = await agent.make_decision(context={"budget_required": amount})
        print(f"  ${amount:>6,} → approved={d['decision']['approved']}")

    await agent.stop()
    print("\n=== Custom Decision Logic Demo complete ===\n")


async def main() -> None:
    await demo_leadership_agent()
    await demo_custom_decision_logic()


if __name__ == "__main__":
    asyncio.run(main())
