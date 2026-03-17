"""
Basic usage example for cmo-agent.

Demonstrates:
- Creating a CMOAgent with default and custom configuration
- Dual-purpose execution (marketing vs leadership adapters)
- Purpose-to-adapter mapping
- Full status query
- Decision making (inherited from LeadershipAgent)
- Goal tracking (inherited from PurposeDrivenAgent)
- Graceful shutdown
"""

from __future__ import annotations

import asyncio
import logging

from cmo_agent import CMOAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def demo_cmo_agent() -> None:
    """Demonstrate CMOAgent dual-purpose capabilities."""
    print("\n=== CMO Agent Demo ===\n")

    cmo = CMOAgent(
        agent_id="cmo-001",
        name="Chief Marketing Officer",
        marketing_purpose=(
            "Marketing: Build category leadership, drive demand generation, "
            "and deliver outstanding customer experiences"
        ),
        leadership_purpose=(
            "Leadership: Lead the marketing organisation and align "
            "cross-functional growth initiatives"
        ),
        purpose_scope="Marketing and cross-functional leadership",
        success_criteria=[
            "Grow MQL pipeline by 40% year-over-year",
            "Improve NPS by 15 points",
            "Launch 4 major campaigns per year",
            "Build high-performing marketing team of 25+",
        ],
        marketing_adapter_name="marketing",
        leadership_adapter_name="leadership",
    )

    print(f"Agent:    {cmo.agent_id} ({cmo.name})")
    print(f"Role:     {cmo.role}")
    print(f"Personas: {cmo.get_agent_type()}")
    print(f"Primary adapter: {cmo.adapter_name}")
    print(f"Purpose adapter mapping: {cmo.purpose_adapter_mapping}")

    # ------------------------------------------------------------------
    # Initialise and start
    # ------------------------------------------------------------------

    print("\n--- Initialising ---")
    ok = await cmo.initialize()
    print(f"Initialised: {ok}")

    ok = await cmo.start()
    print(f"Running:     {ok}")

    # ------------------------------------------------------------------
    # Purpose-specific adapter lookup
    # ------------------------------------------------------------------

    print("\n--- Adapter lookup ---")
    for pt in ("marketing", "leadership"):
        adapter = cmo.get_adapter_for_purpose(pt)
        print(f"  {pt:12} → adapter: {adapter}")

    # ------------------------------------------------------------------
    # Execute with marketing adapter
    # ------------------------------------------------------------------

    print("\n--- Marketing execution ---")
    marketing_tasks = [
        {"type": "brand_audit",      "data": {"brand": "AcmeCorp"}},
        {"type": "campaign_launch",  "data": {"name": "Summer Promo", "budget": 50_000}},
        {"type": "market_analysis",  "data": {"region": "EMEA"}},
    ]
    for task in marketing_tasks:
        result = await cmo.execute_with_purpose(task, purpose_type="marketing")
        print(
            f"  {task['type']:24} → status={result['status']}, "
            f"adapter={result['adapter_used']}"
        )

    # ------------------------------------------------------------------
    # Execute with leadership adapter
    # ------------------------------------------------------------------

    print("\n--- Leadership execution ---")
    leadership_tasks = [
        {"type": "budget_review",      "data": {"quarter": "Q2"}},
        {"type": "team_alignment",     "data": {"attendees": ["vp-sales", "vp-product"]}},
    ]
    for task in leadership_tasks:
        result = await cmo.execute_with_purpose(task, purpose_type="leadership")
        print(
            f"  {task['type']:24} → status={result['status']}, "
            f"adapter={result['adapter_used']}"
        )

    print(f"\n  Primary adapter after all executions: {cmo.adapter_name}")  # should be "marketing"

    # ------------------------------------------------------------------
    # Invalid purpose type
    # ------------------------------------------------------------------

    print("\n--- Invalid purpose type ---")
    try:
        await cmo.execute_with_purpose({"type": "test"}, purpose_type="finance")
    except ValueError as exc:
        print(f"  Expected ValueError: {exc}")

    # ------------------------------------------------------------------
    # Decisions (inherited from LeadershipAgent)
    # ------------------------------------------------------------------

    print("\n--- Decisions ---")
    decision = await cmo.make_decision(
        context={
            "campaign": "Q3 Product Launch",
            "budget_requested": 250_000,
            "expected_leads": 5_000,
        },
        mode="autonomous",
    )
    print(f"  Decision ID:  {decision['id'][:8]}…")
    print(f"  Mode:         {decision['mode']}")

    # ------------------------------------------------------------------
    # Goals
    # ------------------------------------------------------------------

    print("\n--- Goals ---")
    goal_id = await cmo.add_goal(
        "Launch Q3 awareness campaign",
        success_criteria=["Creative assets approved", "Ads live", "10K impressions"],
    )
    await cmo.update_goal_progress(goal_id, 0.33, "Creative assets approved")
    await cmo.update_goal_progress(goal_id, 0.66, "Ads live")
    await cmo.update_goal_progress(goal_id, 1.0,  "10K impressions reached!")
    print(f"  Goals achieved: {cmo.purpose_metrics['goals_achieved']}")

    # ------------------------------------------------------------------
    # Full status
    # ------------------------------------------------------------------

    print("\n--- Full CMO Status ---")
    status = await cmo.get_status()
    print(f"  Agent type:    {status['agent_type']}")
    print(f"  Primary adapter: {status['primary_adapter']}")
    for pt, info in status["purposes"].items():
        print(f"  Purpose '{pt}': adapter={info['adapter']}")
    print(f"  Events processed: {status['total_events_processed']}")
    print(f"  Goals achieved:   {status['metrics']['goals_achieved']}")

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    print("\n--- Stopping ---")
    ok = await cmo.stop()
    print(f"Stopped gracefully: {ok}")

    print("\n=== Demo complete ===\n")


async def main() -> None:
    await demo_cmo_agent()


if __name__ == "__main__":
    asyncio.run(main())
