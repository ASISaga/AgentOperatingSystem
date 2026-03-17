"""
Example: ML Pipeline and LoRAx Multi-Adapter Serving

Demonstrates how to use MLPipelineManager, LoRAxServer, and LoRAxAdapterRegistry
to train LoRA adapters and serve them concurrently on a single GPU.

Prerequisites:
    pip install "aos-intelligence[ml]"
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_ml_pipeline():
    """Example: training a LoRA adapter via MLPipelineManager."""
    print("\n" + "=" * 70)
    print("Example 1: ML Pipeline Manager")
    print("=" * 70 + "\n")

    from aos_intelligence.config import MLConfig
    from aos_intelligence.ml import MLPipelineManager

    config = MLConfig(
        enable_training=True,
        enable_lorax=True,
        model_storage_path="/tmp/models",
        training_data_path="/tmp/training_data",
    )
    pipeline = MLPipelineManager(config)

    print("Triggering LoRA adapter training for 'finance' domain...")
    job_id = await pipeline.train_model({
        "model_type": "lora",
        "adapter_name": "finance",
        "training_data_path": "/tmp/training_data/finance.jsonl",
        "output_dir": "/tmp/models/finance_v1",
    })
    print(f"  Training job ID: {job_id}")

    status = await pipeline.get_training_status(job_id)
    print(f"  Job status: {status['status'] if status else 'unknown'}")

    models = await pipeline.list_models()
    print(f"  Registered models: {len(models)}")


async def example_lorax_server():
    """Example: LoRAx multi-adapter serving."""
    print("\n" + "=" * 70)
    print("Example 2: LoRAx Multi-Adapter Server")
    print("=" * 70 + "\n")

    from aos_intelligence.ml.lorax_server import LoRAxServer, LoRAxConfig

    config = LoRAxConfig(
        base_model="meta-llama/Llama-3.3-70B-Instruct",
        port=8080,
        adapter_cache_size=100,
        max_concurrent_requests=128,
    )
    server = LoRAxServer(config)

    # Register adapters for different agent roles
    server.adapter_registry.register_adapter("ceo_adapter", "CEO", "/models/leadership_v1")
    server.adapter_registry.register_adapter("cmo_adapter", "CMO", "/models/marketing_v1")
    server.adapter_registry.register_adapter("cfo_adapter", "CFO", "/models/finance_v1")

    print(f"Registered {len(server.adapter_registry.list_adapters())} adapters")

    # Inference with adapter selection
    result = await server.inference("ceo_adapter", "What is our Q3 growth strategy?")
    print(f"  CEO response: {result.get('response', result.get('error', 'N/A'))[:80]}")

    # Get server status
    status = server.get_status()
    print(f"  Server status: {status}")


async def example_inference_pipeline():
    """Example: end-to-end inference via the pipeline manager."""
    print("\n" + "=" * 70)
    print("Example 3: Inference via Pipeline Manager")
    print("=" * 70 + "\n")

    from aos_intelligence.config import MLConfig
    from aos_intelligence.ml import MLPipelineManager

    config = MLConfig(enable_training=False, enable_lorax=True)
    pipeline = MLPipelineManager(config)

    # Register an existing LoRA adapter
    pipeline.register_lorax_adapter("legal", "/models/legal_v2")

    result = await pipeline.lorax_inference("legal", "Summarise the key risk clauses in the NDA")
    print(f"  Legal response: {result.get('response', result.get('error', 'N/A'))[:80]}")


async def main():
    await example_ml_pipeline()
    await example_lorax_server()
    await example_inference_pipeline()
    print("\nAll examples completed.")


if __name__ == "__main__":
    asyncio.run(main())
