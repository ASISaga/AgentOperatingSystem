# DPO (Direct Preference Optimization) for Agent Operating System

## Overview

This implementation provides **cost-effective reinforcement learning** for Llama-3.1-8B-Instruct using **Direct Preference Optimization (DPO)**, the industry standard for low-cost alignment.

### Key Benefits

- **30-50% Cost Reduction**: Compared to traditional PPO (Proximal Policy Optimization)
- **No Reward Model**: Eliminates the need to train or host a separate reward model
- **More Stable Training**: Direct optimization is more stable than reward-model-based RLHF
- **Azure Native**: Fully integrated with Azure AI Foundry and Azure ML
- **LoRA Compatible**: Works seamlessly with existing LoRA adapters

## How DPO Works

DPO treats the language model itself as the reward model, optimizing directly on paired preference data:

```
Traditional RLHF (PPO):
1. Train Reward Model (8B params) ← Expensive!
2. Use Reward Model during training ← Memory intensive!
3. Optimize policy with PPO ← Complex!

DPO:
1. Optimize directly on preferences ← Simple!
   (No reward model needed)
```

### Cost Comparison

**Per Training Run (Azure ML Low-Priority NC6s_v3):**

| Method | Reward Model | Policy Training | Total Cost | Total Time |
|--------|--------------|-----------------|------------|------------|
| PPO    | $2.40-3.60   | $6.00-9.60     | $8.40-13.20| 7-11 hours |
| DPO    | -            | $3.60-6.00     | $3.60-6.00 | 3-5 hours  |
| **Savings** | **100%** | **40-60%**     | **40-55%** | **40-55%** |

**Annual Cost (10 agents, monthly retraining):**
- PPO: ~$1,200/year
- DPO: ~$600/year
- **Savings: $600/year (50%)**

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Preference Data Collection                 │
│  Human Rankings | Teacher Model | Automated Heuristics     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│               DPO Training (Azure ML)                       │
│  - Low-Priority NC-Series VM (80% cost savings)            │
│  - TRL DPOTrainer with existing LoRA adapter               │
│  - MLflow tracking for implicit rewards                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│          Model Registry & Deployment                        │
│  - Azure ML Model Registry (versioning)                    │
│  - AI Foundry Serverless API (pay-per-token)               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Install AOS with ML dependencies (includes DPO support)
pip install -e ".[ml]"

# Verify installation
python -c "from AgentOperatingSystem.ml.dpo_trainer import DPOTrainer; print('DPO available!')"
```

### 2. Collect Preference Data

```python
from AgentOperatingSystem.ml.pipeline import MLPipelineManager
from AgentOperatingSystem.config.ml import MLConfig

ml_manager = MLPipelineManager(MLConfig())

# Collect human preference
ml_manager.collect_preference_data(
    agent_role="CEO",
    prompt="What is our Q2 strategy?",
    response_a="We should expand markets.",
    response_b="We should implement a data-driven market expansion strategy "
               "focusing on Europe and Asia with Q2 launch targets.",
    preference="b",  # B is more specific and actionable
    metadata={
        "rater": "strategic_advisor",
        "confidence": "high"
    }
)
```

### 3. Train DPO Adapter

```python
# Train DPO adapter on top of existing LoRA
job_id = await ml_manager.train_dpo_adapter(
    agent_role="CEO",
    base_adapter_path="models/ceo_lora_adapter",
    preference_data_path="preference_data/ceo_preferences.jsonl",
    output_dir="models/ceo_dpo_adapter"
)

# Monitor training
status = ml_manager.get_training_status(job_id)
print(f"Status: {status['status']}, Metrics: {status['metrics']}")
```

### 4. Deploy and Use

```python
# DPO adapter is automatically registered in Azure ML Model Registry
# Deploy via AI Foundry Serverless API
# Use just like any other LoRA adapter

# Check DPO status
dpo_status = ml_manager.get_dpo_status("CEO")
print(f"DPO Adapter Ready: {dpo_status['has_dpo_adapter']}")
```

## Detailed Usage

### Preference Data Collection

DPO requires pairwise preferences: (prompt, chosen_response, rejected_response)

#### Method 1: Human Feedback

```python
from AgentOperatingSystem.ml.dpo_trainer import PreferenceDataCollector

collector = PreferenceDataCollector("preference_data/ceo_preferences.jsonl")

collector.add_human_preference(
    prompt="Analyze Q2 market trends",
    response_a="Markets are looking good.",
    response_b="Q2 shows 15% growth in tech sector, 8% in retail. "
               "Key drivers: digital transformation and consumer confidence.",
    preference="b",
    metadata={"rater": "analyst", "confidence": "high"}
)

collector.save_preferences()
```

#### Method 2: Teacher Model Ranking

```python
# Use advanced model (e.g., Llama 4) to rank responses
await collector.add_teacher_model_preference(
    prompt="Explain revenue forecasting",
    response_a=model_a_output,
    response_b=model_b_output,
    teacher_model="llama-4"
)
```

#### Method 3: Automated Heuristics (Bootstrap)

```python
# Use heuristics for initial data collection
collector.add_heuristic_preference(
    prompt="Describe our product",
    response_a=short_response,
    response_b=detailed_response,
    heuristic="length"  # Prefer more detailed
)
```

### Advanced DPO Configuration

```python
from AgentOperatingSystem.ml.dpo_trainer import DPOTrainer, DPOConfig

# Custom DPO configuration
dpo_config = DPOConfig(
    base_model="meta-llama/Llama-3.1-8B-Instruct",
    lora_adapter_path="models/ceo_lora_adapter",
    
    # DPO hyperparameters
    beta=0.1,              # Temperature (0.05-0.2)
    learning_rate=5e-5,
    num_epochs=3,
    batch_size=4,
    
    # LoRA configuration
    lora_r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    
    # Azure ML
    compute_target="Low-Priority-NC-Series",
    max_length=2048
)

trainer = DPOTrainer(dpo_config)

# Train with MLflow tracking
result = trainer.train(
    preference_data=preferences,
    output_dir="models/ceo_dpo_adapter",
    mlflow_experiment_name="aos_dpo_ceo"
)
```

## Integration with AOS Components

### With Self-Learning System

```python
from AgentOperatingSystem.ml.self_learning_system import SelfLearningSystem

# Self-learning automatically collects preferences
self_learning = SelfLearningSystem(ml_manager)

# Record feedback during agent execution
await self_learning.record_episode(
    agent_id="ceo_agent",
    episode_data={
        "prompt": prompt,
        "response": response,
        "feedback": {"rating": 5, "preferred": True}
    }
)

# Trigger DPO training when enough data collected
if self_learning.should_run_dpo_training("CEO"):
    await ml_manager.train_dpo_adapter(
        agent_role="CEO",
        base_adapter_path="models/ceo_lora_adapter",
        preference_data_path=self_learning.get_preference_data_path("CEO")
    )
```

### With Knowledge Base (RAG)

```python
from AgentOperatingSystem.learning.rag_engine import RAGEngine

# Generate comparison responses
response_standard = await agent.generate(prompt)
response_rag = await rag_engine.generate_response(prompt)

# Collect preference (RAG usually better)
ml_manager.collect_preference_data(
    agent_role="CEO",
    prompt=prompt,
    response_a=response_standard,
    response_b=response_rag,
    preference="b"  # RAG-enhanced
)
```

## MLflow Tracking

DPO training automatically tracks metrics to MLflow:

**Tracked Metrics:**
- `train_loss`: Overall DPO loss
- `implicit_reward`: Computed from preference pairs
- `accuracy`: Preference prediction accuracy
- `convergence`: Gradient norms

**View in MLflow UI:**
```bash
# Start MLflow UI
mlflow ui --backend-store-uri azureml://...

# Navigate to http://localhost:5000
# View experiment: aos_dpo_{agent_role}
```

## Azure ML Deployment

### 1. Train on Low-Priority Compute

```python
# Configured in DPOConfig
compute_target="Low-Priority-NC-Series"  # 80% cost savings!
```

### 2. Register in Model Registry

```python
# Automatic registration after training
# Or manual:
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model

ml_client = MLClient(...)
model = Model(
    path="models/ceo_dpo_adapter",
    name="ceo-dpo-llama-3.1-8b",
    version="1.0.0",
    description="DPO-aligned LoRA for CEO agent"
)
ml_client.models.create_or_update(model)
```

### 3. Deploy to AI Foundry Serverless

```python
# Deploy to serverless endpoint (pay-per-token)
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment

endpoint = ManagedOnlineEndpoint(name="ceo-dpo-endpoint")
deployment = ManagedOnlineDeployment(
    name="ceo-dpo",
    endpoint_name="ceo-dpo-endpoint",
    model=model
)

ml_client.online_endpoints.begin_create_or_update(endpoint)
ml_client.online_deployments.begin_create_or_update(deployment)
```

## Best Practices

### Data Collection

1. **Aim for 500-1000+ preference pairs** for meaningful alignment
2. **Ensure diverse prompts** covering the agent's domain
3. **Balance human and automated preferences** (80/20 recommended)
4. **Regular quality audits** of collected data

### Training

1. **Start with existing LoRA adapter** (task-specific)
2. **Apply DPO as secondary alignment layer**
3. **Use low beta (0.05-0.1)** for subtle adjustments
4. **Monitor convergence** via MLflow

### Cost Optimization

1. **Use Low-Priority/Spot instances** (80% savings)
2. **Batch multiple agents' training** together
3. **Schedule during off-peak hours**
4. **Leverage checkpoint resume** for interrupted jobs

### Deployment

1. **A/B test** DPO vs base adapter
2. **Monitor user satisfaction** post-deployment
3. **Keep base adapter as fallback**
4. **Version control all adapters**

## Security Considerations

**Data Privacy:**
- Encrypt preference data at rest and in transit
- Implement access controls for collection
- Audit data access regularly

**Model Security:**
- Validate preference data sources
- Prevent adversarial injection
- Monitor for reward hacking
- Implement content safety filters

## Troubleshooting

### Issue: "TRL library not available"
```bash
pip install trl transformers peft accelerate
```

### Issue: "Out of memory during training"
- Reduce `batch_size` (try 2 or 1)
- Increase `gradient_accumulation_steps`
- Use smaller LoRA rank (`lora_r=8`)

### Issue: "Preference data not found"
```python
# Check preference file exists
from pathlib import Path
pref_path = Path("preference_data/ceo_preferences.jsonl")
print(f"Exists: {pref_path.exists()}")

# Verify format
with open(pref_path) as f:
    print(f.readline())  # Should be JSON
```

### Issue: "Training not converging"
- Increase `beta` (try 0.2)
- Check preference data quality
- Ensure preferences are consistent
- Try more training epochs

## Examples

See `examples/dpo_training_example.py` for complete examples:

```bash
python examples/dpo_training_example.py
```

## Documentation

- **Specification**: `docs/specifications/ml.md` (Section 8)
- **API Reference**: See docstrings in `src/AgentOperatingSystem/ml/dpo_trainer.py`
- **Example Code**: `examples/dpo_training_example.py`

## References

- [DPO Paper](https://arxiv.org/abs/2305.18290): "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
- [TRL Library](https://github.com/huggingface/trl): Transformer Reinforcement Learning
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry)
- [Azure ML](https://azure.microsoft.com/en-us/products/machine-learning/)

## Support

For issues or questions:
1. Check this README and `docs/specifications/ml.md`
2. Review examples in `examples/dpo_training_example.py`
3. Open an issue on GitHub
4. Contact the AOS ML Team

---

**Document Version:** 1.0.0  
**Last Updated:** December 25, 2025  
**Status:** Production Ready
