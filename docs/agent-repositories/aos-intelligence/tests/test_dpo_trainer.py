"""
Tests for DPOTrainer and PreferenceData.
"""

import pytest
from aos_intelligence.ml.dpo_trainer import (
    DPOTrainer, DPOConfig, PreferenceData, PreferenceDataCollector
)


class TestDPOConfig:
    def test_default_config(self):
        config = DPOConfig()
        assert config.base_model == "meta-llama/Llama-3.3-70B-Instruct"
        assert config.beta == 0.1
        assert config.num_epochs == 3
        assert config.batch_size == 4

    def test_custom_config(self):
        config = DPOConfig(beta=0.2, num_epochs=5, learning_rate=1e-4)
        assert config.beta == 0.2
        assert config.num_epochs == 5
        assert config.learning_rate == 1e-4


class TestPreferenceData:
    def test_creation(self):
        pref = PreferenceData(
            prompt="What is our Q2 strategy?",
            chosen_response="Focus on European market expansion.",
            rejected_response="I think we need to consider things.",
        )
        assert pref.prompt == "What is our Q2 strategy?"
        assert "European" in pref.chosen_response

    def test_with_metadata(self):
        pref = PreferenceData(
            prompt="Summarise the risk",
            chosen_response="The main risk is X.",
            rejected_response="There are risks.",
            metadata={"domain": "finance", "confidence": "high"},
        )
        assert pref.metadata["domain"] == "finance"


class TestPreferenceDataCollector:
    def test_add_human_preference(self, tmp_path):
        collector = PreferenceDataCollector(
            storage_path=str(tmp_path / "prefs.jsonl")
        )
        collector.add_human_preference(
            prompt="Test prompt",
            response_a="Response A",
            response_b="Response B",
            preference="a",
        )
        prefs = collector.get_preferences()
        assert len(prefs) == 1
        assert prefs[0].chosen_response == "Response A"

    def test_add_heuristic_preference(self, tmp_path):
        collector = PreferenceDataCollector(
            storage_path=str(tmp_path / "prefs2.jsonl")
        )
        collector.add_heuristic_preference(
            prompt="Explain the methodology",
            good_response="Our methodology is based on three pillars: X, Y, Z.",
            bad_response="We have a methodology.",
        )
        prefs = collector.get_preferences()
        assert len(prefs) == 1

    def test_get_training_data(self, tmp_path):
        collector = PreferenceDataCollector(
            storage_path=str(tmp_path / "prefs3.jsonl")
        )
        collector.add_human_preference("P1", "A1", "B1", "a")
        collector.add_human_preference("P2", "A2", "B2", "b")
        data = collector.get_training_data()
        assert len(data) == 2


class TestDPOTrainer:
    def test_creation(self):
        config = DPOConfig()
        trainer = DPOTrainer(config)
        assert trainer.config is config

    @pytest.mark.asyncio
    async def test_train_empty_data(self):
        config = DPOConfig()
        trainer = DPOTrainer(config)
        result = await trainer.train([])
        assert isinstance(result, dict)
        assert "status" in result
