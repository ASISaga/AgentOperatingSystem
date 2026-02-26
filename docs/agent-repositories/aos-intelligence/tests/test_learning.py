"""
Tests for the learning module: KnowledgeManager, RAGEngine, InteractionLearner, LearningPipeline.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aos_intelligence.learning.knowledge_manager import KnowledgeManager
from aos_intelligence.learning.rag_engine import RAGEngine
from aos_intelligence.learning.interaction_learner import InteractionLearner


def _make_mock_storage():
    """Create a mock storage manager."""
    storage = MagicMock()
    storage.exists = AsyncMock(return_value=False)
    storage.read_json = AsyncMock(return_value={})
    storage.write_json = AsyncMock()
    return storage


class TestKnowledgeManager:
    @pytest.mark.asyncio
    async def test_initialize(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage, config={})
        await km.initialize()
        assert len(km.domain_contexts) > 0

    @pytest.mark.asyncio
    async def test_get_domain_context_default(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage)
        await km.initialize()
        ctx = await km.get_domain_context("sales")
        assert "purpose" in ctx

    @pytest.mark.asyncio
    async def test_get_missing_domain_falls_back_to_general(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage)
        await km.initialize()
        ctx = await km.get_domain_context("nonexistent_domain")
        assert ctx  # should return general context

    @pytest.mark.asyncio
    async def test_get_agent_directives(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage)
        await km.initialize()
        directive = await km.get_agent_directives("leadership")
        assert isinstance(directive, str)
        assert len(directive) > 0

    @pytest.mark.asyncio
    async def test_add_knowledge_entry(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage)
        await km.initialize()
        await km.add_knowledge_entry("sales", {
            "title": "Test entry",
            "content": "Test content",
        })
        entries = await km.get_domain_knowledge("sales")
        assert any(e.get("title") == "Test entry" for e in entries)

    @pytest.mark.asyncio
    async def test_get_knowledge_summary(self):
        storage = _make_mock_storage()
        km = KnowledgeManager(storage_manager=storage)
        await km.initialize()
        summary = await km.get_knowledge_summary()
        assert "domains" in summary
        assert "knowledge_entries" in summary


class TestRAGEngine:
    def test_creation(self):
        rag = RAGEngine(config={
            "vector_db_host": "localhost",
            "vector_db_port": 8000,
        })
        assert rag.vector_db_host == "localhost"
        assert rag.vector_db_port == 8000

    def test_default_config(self):
        rag = RAGEngine()
        assert rag.top_k_default == 5
        assert rag.min_similarity == 0.7


class TestInteractionLearner:
    @pytest.mark.asyncio
    async def test_initialize(self):
        storage = _make_mock_storage()
        learner = InteractionLearner(storage_manager=storage)
        await learner.initialize()
        assert learner.interaction_history == []

    @pytest.mark.asyncio
    async def test_log_interaction(self):
        storage = _make_mock_storage()
        learner = InteractionLearner(storage_manager=storage)
        await learner.initialize()
        await learner.log_interaction(
            agent_id="agent-001",
            user_input="What are the top leads?",
            response="Here are the top 5 leads...",
            domain="sales",
            conversation_id="conv-001",
        )
        assert len(learner.interaction_history) == 1

    @pytest.mark.asyncio
    async def test_add_feedback(self):
        storage = _make_mock_storage()
        learner = InteractionLearner(storage_manager=storage)
        await learner.initialize()
        await learner.log_interaction(
            agent_id="agent-001",
            user_input="Help me with Q2 planning",
            response="Here is the Q2 plan...",
            domain="leadership",
            conversation_id="conv-002",
        )
        result = await learner.add_feedback("conv-002", rating=4.5)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_domain_insights(self):
        storage = _make_mock_storage()
        learner = InteractionLearner(storage_manager=storage)
        await learner.initialize()
        insights = await learner.get_domain_insights("sales")
        assert "domain" in insights
        assert insights["domain"] == "sales"

    @pytest.mark.asyncio
    async def test_get_recent_interactions_filtered(self):
        storage = _make_mock_storage()
        learner = InteractionLearner(storage_manager=storage)
        await learner.initialize()
        await learner.log_interaction("a1", "Q1", "R1", "sales", "c1")
        await learner.log_interaction("a2", "Q2", "R2", "crm", "c2")
        sales = await learner.get_recent_interactions(domain="sales")
        assert len(sales) == 1
        assert sales[0]["domain"] == "sales"
