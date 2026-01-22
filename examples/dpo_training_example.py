"""
Example: DPO (Direct Preference Optimization) Training for AOS Agents

This example demonstrates how to use DPO for cost-effective reinforcement learning
from human feedback, achieving 30-50% cost reduction compared to traditional PPO.

DPO Implementation Workflow:
1. Collect preference data (human rankings, teacher model, or heuristics)
2. Train DPO adapter on top of existing LoRA adapter
3. Monitor training with MLflow
4. Deploy DPO-aligned model to production

Prerequisites:
- pip install transformers trl peft torch mlflow
- Azure ML workspace configured
- Existing LoRA adapter for the target agent
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_preference_data_collection():
    """
    Example 1: Collecting preference data for DPO training
    """
    print("\n" + "="*80)
    print("Example 1: Preference Data Collection")
    print("="*80 + "\n")
    
    from AgentOperatingSystem.ml.dpo_trainer import PreferenceDataCollector
    
    # Initialize collector
    collector = PreferenceDataCollector(
        storage_path="preference_data/ceo_preferences.jsonl"
    )
    
    # Method 1: Human feedback
    print("1. Collecting human preference...")
    collector.add_human_preference(
        prompt="What is our strategic vision for Q2 2025?",
        response_a="We should focus on market expansion in Europe and Asia.",
        response_b="I think we need to consider various factors.",
        preference="a",  # Response A is more specific and actionable
        metadata={
            "rater": "strategic_advisor",
            "confidence": "high",
            "domain": "strategy"
        }
    )
    
    # Method 2: Heuristic-based preference (for bootstrapping)
    print("2. Collecting heuristic preference...")
    collector.add_heuristic_preference(
        prompt="Explain our revenue forecasting methodology",
        response_a="We use historical data and trends.",
        response_b="We use a comprehensive approach that combines historical data analysis, "
                   "market trend evaluation, competitive intelligence, and predictive modeling "
                   "to generate quarterly revenue forecasts with 95% confidence intervals.",
        heuristic="length",  # Prefer more detailed responses
        metadata={"source": "bootstrap"}
    )
    
    # Method 3: Teacher model (conceptual - requires implementation)
    print("3. Teacher model preference (conceptual)...")
    # await collector.add_teacher_model_preference(
    #     prompt="Analyze market opportunities in Southeast Asia",
    #     response_a=response_from_model_a,
    #     response_b=response_from_model_b,
    #     teacher_model="llama-4"
    # )
    
    # Save preferences
    saved_path = collector.save_preferences()
    print(f"\n✓ Collected {len(collector.preferences)} preferences")
    print(f"✓ Saved to: {saved_path}")
    
    return saved_path


async def example_dpo_training_basic():
    """
    Example 2: Basic DPO training using MLPipelineManager
    """
    print("\n" + "="*80)
    print("Example 2: Basic DPO Training")
    print("="*80 + "\n")
    
    from AgentOperatingSystem.ml.pipeline import MLPipelineManager
    from AgentOperatingSystem.config.ml import MLConfig
    
    # Configure ML pipeline with DPO enabled
    config = MLConfig()
    config.enable_dpo = True
    config.enable_mlflow = True
    config.mlflow_experiment_prefix = "aos_dpo_example"
    config.preference_data_path = "preference_data"
    
    ml_manager = MLPipelineManager(config)
    
    print("Starting DPO training...")
    print("  Agent Role: CEO")
    print("  Base Adapter: models/ceo_lora_adapter")
    print("  Preference Data: preference_data/ceo_preferences.jsonl")
    print()
    
    # Note: This requires actual model files and preference data
    # For demonstration, we show the API usage
    try:
        job_id = await ml_manager.train_dpo_adapter(
            agent_role="CEO",
            base_adapter_path="models/ceo_lora_adapter",
            preference_data_path="preference_data/ceo_preferences.jsonl",
            output_dir="models/ceo_dpo_adapter",
            config_override={
                "beta": 0.1,           # Conservative alignment
                "learning_rate": 5e-5,
                "batch_size": 4,
                "num_epochs": 3
            }
        )
        
        print(f"✓ Training job started: {job_id}")
        
        # Monitor training
        while True:
            await asyncio.sleep(5)
            status = ml_manager.get_training_status(job_id)
            print(f"  Status: {status['status']}")
            
            if status['status'] in ['completed', 'failed']:
                if status['status'] == 'completed':
                    print(f"\n✓ Training completed!")
                    print(f"  Metrics: {status.get('metrics', {})}")
                    print(f"  Model Path: {status.get('model_path')}")
                else:
                    print(f"\n✗ Training failed: {status.get('error')}")
                break
                
    except Exception as e:
        print(f"Note: Training not executed in example mode: {e}")
        print("This example requires actual model files and Azure ML setup.")


async def example_dpo_training_advanced():
    """
    Example 3: Advanced DPO training with custom configuration
    """
    print("\n" + "="*80)
    print("Example 3: Advanced DPO Training")
    print("="*80 + "\n")
    
    from AgentOperatingSystem.ml.dpo_trainer import (
        DPOTrainer, DPOConfig, PreferenceDataCollector
    )
    
    # Load preference data
    print("Loading preference data...")
    collector = PreferenceDataCollector()
    try:
        collector.load_preferences("preference_data/ceo_preferences.jsonl")
        preferences = collector.get_preferences()
        print(f"✓ Loaded {len(preferences)} preference pairs")
    except Exception as e:
        print(f"Note: Could not load preferences: {e}")
        print("Creating sample preferences for demonstration...")
        
        # Create sample preferences
        from AgentOperatingSystem.ml.dpo_trainer import PreferenceData
        preferences = [
            PreferenceData(
                prompt="What is our Q2 strategy?",
                chosen_response="Focus on market expansion with data-driven approach.",
                rejected_response="We should do something about Q2.",
                metadata={"source": "sample"}
            )
        ]
    
    # Configure DPO training
    print("\nConfiguring DPO training...")
    dpo_config = DPOConfig(
        base_model="meta-llama/Llama-3.3-70B-Instruct",
        lora_adapter_path="models/ceo_lora_adapter",  # Existing LoRA
        
        # DPO hyperparameters
        beta=0.1,                    # Temperature parameter
        learning_rate=5e-5,
        num_epochs=3,
        batch_size=4,
        gradient_accumulation_steps=4,
        
        # LoRA configuration for DPO layer
        lora_r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        lora_target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        
        # Infrastructure
        compute_target="Low-Priority-NC-Series",
        max_length=2048,
        max_prompt_length=1024,
        
        # Training control
        warmup_steps=100,
        logging_steps=10,
        save_steps=500,
        eval_steps=100
    )
    
    print("DPO Configuration:")
    print(f"  Beta (temperature): {dpo_config.beta}")
    print(f"  Learning rate: {dpo_config.learning_rate}")
    print(f"  LoRA rank: {dpo_config.lora_r}")
    print(f"  Batch size: {dpo_config.batch_size}")
    print(f"  Epochs: {dpo_config.num_epochs}")
    
    # Initialize trainer
    print("\nInitializing DPO trainer...")
    trainer = DPOTrainer(dpo_config)
    
    # Train (note: requires actual models and GPU)
    print("\nTraining (requires GPU and model files)...")
    try:
        result = trainer.train(
            preference_data=preferences,
            output_dir="models/ceo_dpo_adapter",
            mlflow_experiment_name="aos_dpo_ceo_advanced"
        )
        
        print("\n✓ Training completed!")
        print(f"  Status: {result['status']}")
        print(f"  Output: {result['output_dir']}")
        print(f"  Metrics: {result['metrics']}")
        
    except Exception as e:
        print(f"Note: Training not executed: {e}")
        print("This example requires actual model files, GPU, and dependencies.")


async def example_preference_collection_workflow():
    """
    Example 4: Complete preference collection workflow with ML pipeline
    """
    print("\n" + "="*80)
    print("Example 4: Preference Collection Workflow")
    print("="*80 + "\n")
    
    from AgentOperatingSystem.ml.pipeline import MLPipelineManager
    from AgentOperatingSystem.config.ml import MLConfig
    
    ml_manager = MLPipelineManager(MLConfig())
    
    # Scenario: CEO agent generates responses, users provide feedback
    print("Scenario: Collecting preferences from user interactions")
    print()
    
    # Simulate agent generating two responses
    prompt = "What should be our pricing strategy for the new product?"
    response_conservative = "We should maintain competitive pricing aligned with market standards."
    response_detailed = """We should implement a value-based pricing strategy that considers:
    1. Customer willingness to pay based on perceived value
    2. Competitor pricing and market positioning
    3. Cost structure and desired profit margins
    4. Price elasticity in our target segments
    5. Initial penetration pricing with gradual optimization
    
    I recommend starting at $99/month with a 20% introductory discount."""
    
    # User prefers the detailed response
    print(f"Prompt: {prompt[:60]}...")
    print(f"Response A (Conservative): {response_conservative[:60]}...")
    print(f"Response B (Detailed): {response_detailed[:80]}...")
    print(f"User Preference: B (more comprehensive)")
    print()
    
    # Collect preference
    ml_manager.collect_preference_data(
        agent_role="CEO",
        prompt=prompt,
        response_a=response_conservative,
        response_b=response_detailed,
        preference="b",
        metadata={
            "rater": "product_manager",
            "confidence": "high",
            "context": "pricing_strategy",
            "session_id": "sess_12345"
        }
    )
    
    print("✓ Preference collected and saved")
    
    # Check DPO status
    dpo_status = ml_manager.get_dpo_status("CEO")
    print(f"\nDPO Status for CEO:")
    print(f"  Preference Count: {dpo_status['preference_count']}")
    print(f"  Has Preference Data: {dpo_status['has_preference_data']}")
    print(f"  DPO Adapter Status: {dpo_status['status']}")
    
    # When enough preferences collected, trigger training
    if dpo_status['preference_count'] >= 100:  # Example threshold
        print(f"\n✓ Sufficient preferences collected ({dpo_status['preference_count']})")
        print("  Triggering DPO training...")
        # await ml_manager.train_dpo_adapter(...)


async def example_cost_comparison():
    """
    Example 5: Cost comparison between DPO and PPO
    """
    print("\n" + "="*80)
    print("Example 5: DPO vs PPO Cost Comparison")
    print("="*80 + "\n")
    
    print("Training Configuration:")
    print("  Base Model: Llama-3.3-70B-Instruct")
    print("  Compute: Azure ML Low-Priority NC6s_v3 ($1.20/hour)")
    print("  Training Data: 1000 preference pairs")
    print()
    
    print("Traditional PPO (Proximal Policy Optimization):")
    print("  Phase 1: Reward Model Training")
    print("    - Model Size: 70B parameters")
    print("    - Training Time: 2-3 hours")
    print("    - Cost: $2.40-3.60")
    print("  Phase 2: Policy Optimization")
    print("    - Training Time: 5-8 hours (with reward model inference)")
    print("    - Cost: $6.00-9.60")
    print("  Total Cost: $8.40-13.20")
    print("  Total Time: 7-11 hours")
    print()
    
    print("DPO (Direct Preference Optimization):")
    print("  Phase 1: Direct Policy Training")
    print("    - Training Time: 3-5 hours (no reward model needed)")
    print("    - Cost: $3.60-6.00")
    print("  Total Cost: $3.60-6.00")
    print("  Total Time: 3-5 hours")
    print()
    
    print("Savings with DPO:")
    print("  Cost Reduction: 30-50%")
    print("  Time Reduction: 40-55%")
    print("  Memory Savings: ~50% (no reward model)")
    print("  Training Stability: Higher (direct optimization)")
    print()
    
    print("Annual Cost Projection (10 agents, monthly retraining):")
    print(f"  PPO: 10 agents × 12 months × $10 = $1,200/year")
    print(f"  DPO: 10 agents × 12 months × $5 = $600/year")
    print(f"  Annual Savings: $600 (50%)")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("DPO Training Examples for Agent Operating System")
    print("="*80)
    
    # Run examples
    await example_preference_data_collection()
    await example_preference_collection_workflow()
    await example_cost_comparison()
    
    # Advanced examples (require actual infrastructure)
    print("\n" + "="*80)
    print("Advanced Examples (require Azure ML and GPU)")
    print("="*80)
    
    await example_dpo_training_basic()
    await example_dpo_training_advanced()
    
    print("\n" + "="*80)
    print("Examples Complete!")
    print("="*80)
    print("\nNext Steps:")
    print("1. Set up Azure ML workspace and compute")
    print("2. Train initial LoRA adapters for your agents")
    print("3. Collect preference data from user interactions")
    print("4. Run DPO training to align models with preferences")
    print("5. Deploy DPO-aligned adapters to production")
    print("6. Monitor implicit reward metrics in MLflow")
    print("\nFor production deployment, see docs/specifications/ml.md")


if __name__ == "__main__":
    asyncio.run(main())
