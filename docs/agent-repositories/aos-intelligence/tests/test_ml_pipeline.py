"""
Tests for MLPipelineManager and MLConfig.
"""

import pytest
from aos_intelligence.config import MLConfig
from aos_intelligence.ml import MLPipelineManager


class TestMLConfig:
    def test_default_config(self):
        config = MLConfig()
        assert config.enable_training is True
        assert config.enable_lorax is True
        assert config.enable_dpo is True
        assert config.default_model_type == "lora"
        assert config.lorax_port == 8080

    def test_custom_config(self):
        config = MLConfig(
            enable_training=False,
            lorax_port=9090,
            lorax_adapter_cache_size=50,
        )
        assert config.enable_training is False
        assert config.lorax_port == 9090
        assert config.lorax_adapter_cache_size == 50

    def test_from_env_defaults(self, monkeypatch):
        monkeypatch.delenv("AOS_ENABLE_ML_TRAINING", raising=False)
        monkeypatch.delenv("AOS_LORAX_PORT", raising=False)
        config = MLConfig.from_env()
        assert config.enable_training is True
        assert config.lorax_port == 8080

    def test_from_env_overrides(self, monkeypatch):
        monkeypatch.setenv("AOS_ENABLE_ML_TRAINING", "false")
        monkeypatch.setenv("AOS_LORAX_PORT", "9999")
        config = MLConfig.from_env()
        assert config.enable_training is False
        assert config.lorax_port == 9999


class TestMLPipelineManager:
    def test_creation(self, ml_config):
        pipeline = MLPipelineManager(ml_config)
        assert pipeline.config is ml_config

    def test_training_disabled(self, minimal_config):
        pipeline = MLPipelineManager(minimal_config)
        assert pipeline.config.enable_training is False

    @pytest.mark.asyncio
    async def test_train_model_raises_when_disabled(self, minimal_config):
        pipeline = MLPipelineManager(minimal_config)
        with pytest.raises(RuntimeError, match="disabled"):
            await pipeline.train_model({"model_type": "lora"})

    @pytest.mark.asyncio
    async def test_train_model_returns_job_id(self, ml_config):
        pipeline = MLPipelineManager(ml_config)
        job_id = await pipeline.train_model({
            "model_type": "lora",
            "adapter_name": "test_adapter",
            "training_data_path": "/tmp/test_data.jsonl",
            "output_dir": "/tmp/test_output",
        })
        assert isinstance(job_id, str)
        assert len(job_id) > 0

    @pytest.mark.asyncio
    async def test_get_job_status(self, ml_config):
        pipeline = MLPipelineManager(ml_config)
        job_id = await pipeline.train_model({
            "model_type": "lora",
            "adapter_name": "status_test",
            "training_data_path": "/tmp/data.jsonl",
            "output_dir": "/tmp/output",
        })
        status = pipeline.get_training_status(job_id)
        assert status is None or isinstance(status, dict)

    def test_list_models(self, ml_config):
        pipeline = MLPipelineManager(ml_config)
        models = pipeline.list_models()
        assert isinstance(models, list)
