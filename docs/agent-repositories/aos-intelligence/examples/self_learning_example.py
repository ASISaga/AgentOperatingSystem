"""
Example: Self-Learning Agent

Demonstrates how to use the self-learning capabilities of aos-intelligence:
KnowledgeManager, InteractionLearner, and SelfLearningMixin for continuous
agent improvement via feedback.

Prerequisites:
    pip install "aos-intelligence"
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _make_storage():
    """Create an in-memory mock storage manager for this example."""
    storage = MagicMock()
    storage.exists = AsyncMock(return_value=False)
    storage.read_json = AsyncMock(return_value={})
    storage.write_json = AsyncMock()
    return storage


async def example_knowledge_manager():
    """Example: managing domain knowledge."""
    print("\n" + "=" * 70)
    print("Example 1: Knowledge Manager")
    print("=" * 70 + "\n")

    from aos_intelligence.learning import KnowledgeManager

    storage = _make_storage()
    km = KnowledgeManager(storage_manager=storage, config={
        "knowledge_base_path": "knowledge",
    })
    await km.initialize()

    # Get domain context
    ctx = await km.get_domain_context("sales")
    print(f"  Sales domain purpose: {ctx.get('purpose', 'N/A')}")
    print(f"  Sales metrics: {ctx.get('key_metrics', [])}")

    # Add new knowledge
    await km.add_knowledge_entry("sales", {
        "title": "Q2 Enterprise objection handling",
        "content": "When enterprise customers raise budget objections, present 3-year TCO.",
        "tags": ["enterprise", "objections", "TCO"],
    })

    entries = await km.get_domain_knowledge("sales")
    print(f"  Knowledge entries in 'sales': {len(entries)}")

    # Get agent directives
    directive = await km.get_agent_directives("leadership")
    print(f"  Leadership directive (first 80 chars): {directive[:80]}")

    summary = await km.get_knowledge_summary()
    print(f"  Knowledge summary: {summary['domains']}")


async def example_interaction_learning():
    """Example: learning from agent interactions."""
    print("\n" + "=" * 70)
    print("Example 2: Interaction Learner")
    print("=" * 70 + "\n")

    from aos_intelligence.learning import InteractionLearner

    storage = _make_storage()
    learner = InteractionLearner(storage_manager=storage)
    await learner.initialize()

    # Log several interactions
    print("  Logging interactions...")
    for i in range(5):
        await learner.log_interaction(
            agent_id="sales-agent-001",
            user_input=f"What are the top leads for region {i}?",
            response=f"The top leads for region {i} are: Lead A, Lead B, Lead C.",
            domain="sales",
            conversation_id=f"conv-{i:03d}",
        )

    # Add feedback for some interactions
    await learner.add_feedback("conv-000", rating=5.0, feedback="Excellent response!")
    await learner.add_feedback("conv-001", rating=3.5, feedback="Could be more specific")
    await learner.add_feedback("conv-002", rating=4.0)

    # Get insights
    insights = await learner.get_domain_insights("sales")
    print(f"  Total sales interactions: {insights['total_interactions']}")
    if insights["avg_rating"] is not None:
        print(f"  Average rating: {insights['avg_rating']:.2f}")
    print(f"  Recommendations: {insights['recommendations']}")

    # Get learning summary
    summary = await learner.get_learning_summary()
    print(f"  Overall avg rating: {summary.get('avg_rating_overall')}")


async def example_dpo_preference_collection():
    """Example: collecting DPO preference data from interactions."""
    print("\n" + "=" * 70)
    print("Example 3: DPO Preference Collection")
    print("=" * 70 + "\n")

    from aos_intelligence.ml.dpo_trainer import PreferenceDataCollector, DPOTrainer, DPOConfig

    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        storage_path = f.name

    try:
        collector = PreferenceDataCollector(storage_path=storage_path)

        # Collect human preferences
        collector.add_human_preference(
            prompt="What is our strategic vision for Q2 2025?",
            response_a="Focus on market expansion in Europe and Asia with €5M investment.",
            response_b="We should consider various factors and decide later.",
            preference="a",
            metadata={"rater": "strategic_advisor", "confidence": "high"},
        )

        # Collect heuristic-based preferences
        collector.add_heuristic_preference(
            prompt="Explain our revenue forecasting methodology",
            good_response="We use a three-stage model: pipeline analysis, close rate estimation, and seasonal adjustment.",
            bad_response="We forecast revenue.",
        )

        prefs = collector.get_preferences()
        print(f"  Collected {len(prefs)} preference pairs")

        training_data = collector.get_training_data()
        print(f"  Training data entries: {len(training_data)}")

        # Initialise DPO trainer (training requires ML deps: pip install aos-intelligence[ml])
        config = DPOConfig(num_epochs=1, batch_size=2)
        trainer = DPOTrainer(config)
        print(f"  DPO trainer initialised (base model: {config.base_model})")

    finally:
        os.unlink(storage_path)


async def main():
    await example_knowledge_manager()
    await example_interaction_learning()
    await example_dpo_preference_collection()
    print("\nAll examples completed.")


if __name__ == "__main__":
    asyncio.run(main())
