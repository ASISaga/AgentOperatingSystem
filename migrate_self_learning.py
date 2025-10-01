"""
Migration script to extract useful components from SelfLearningAgent
and integrate them into the new AOS learning system.
"""

import os
import shutil
import json
from pathlib import Path

def migrate_knowledge_base():
    """Migrate knowledge base files from SelfLearningAgent"""
    source_dir = Path("c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent")
    aos_dir = Path("c:/Development/ASISaga/RealmOfAgents/AgentOperatingSystem")
    
    # Create knowledge directory in AOS
    knowledge_dir = aos_dir / "knowledge"
    knowledge_dir.mkdir(exist_ok=True)
    
    # Copy knowledge files if they exist
    knowledge_files = [
        "config/domain_contexts.json",
        "config/domain_knowledge.json", 
        "config/agent_directives.json",
        "knowledge/domain_contexts.json",
        "knowledge/domain_knowledge.json",
        "knowledge/agent_directives.json"
    ]
    
    for file_path in knowledge_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = knowledge_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            print(f"Copied {source_file} to {dest_file}")

def migrate_config_files():
    """Migrate configuration files"""
    source_dir = Path("c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent")
    aos_dir = Path("c:/Development/ASISaga/RealmOfAgents/AgentOperatingSystem")
    
    # Create config directory in AOS
    config_dir = aos_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Copy useful config files
    config_files = [
        "config/learning_config.json",
        "config/rag_config.json"
    ]
    
    for file_path in config_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = config_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            print(f"Copied {source_file} to {dest_file}")

def create_sample_knowledge():
    """Create sample knowledge files for the learning system"""
    aos_dir = Path("c:/Development/ASISaga/RealmOfAgents/AgentOperatingSystem")
    knowledge_dir = aos_dir / "knowledge"
    knowledge_dir.mkdir(exist_ok=True)
    
    # Sample domain contexts
    domain_contexts = {
        "sales": {
            "purpose": "Drive revenue growth through customer acquisition and retention",
            "key_metrics": ["conversion_rate", "revenue", "customer_satisfaction"],
            "responsibilities": ["lead_qualification", "proposal_creation", "relationship_building"]
        },
        "leadership": {
            "purpose": "Guide teams and make strategic decisions for organizational success",
            "key_metrics": ["team_performance", "strategic_goals", "stakeholder_satisfaction"],
            "responsibilities": ["strategic_planning", "team_development", "decision_making"]
        },
        "erp": {
            "purpose": "Manage business processes and enterprise resource planning",
            "key_metrics": ["process_efficiency", "data_accuracy", "system_uptime"],
            "responsibilities": ["process_optimization", "data_management", "system_integration"]
        },
        "crm": {
            "purpose": "Manage customer relationships and interactions",
            "key_metrics": ["customer_satisfaction", "retention_rate", "interaction_quality"],
            "responsibilities": ["customer_support", "relationship_management", "data_analysis"]
        },
        "general": {
            "purpose": "Provide general assistance and knowledge across domains",
            "key_metrics": ["response_quality", "user_satisfaction", "knowledge_accuracy"],
            "responsibilities": ["information_retrieval", "general_assistance", "cross_domain_coordination"]
        }
    }
    
    with open(knowledge_dir / "domain_contexts.json", "w") as f:
        json.dump(domain_contexts, f, indent=2)
    print("Created domain_contexts.json")
    
    # Sample agent directives
    agent_directives = {
        "sales": "Focus on understanding customer needs, building relationships, and presenting value propositions that align with business objectives.",
        "leadership": "Prioritize strategic thinking, team empowerment, and data-driven decision making while maintaining stakeholder alignment.",
        "erp": "Ensure process efficiency, data integrity, and seamless system integration while optimizing business operations.",
        "crm": "Maintain customer-centric approach, ensure data accuracy, and provide exceptional service experiences.",
        "general": "Provide accurate, helpful information while maintaining professionalism and seeking clarity when needed."
    }
    
    with open(knowledge_dir / "agent_directives.json", "w") as f:
        json.dump(agent_directives, f, indent=2)
    print("Created agent_directives.json")
    
    # Sample domain knowledge
    domain_knowledge = {
        "sales": [
            {
                "content": "Effective sales qualification involves understanding customer pain points, budget, timeline, and decision-making authority.",
                "type": "best_practice",
                "source": "sales_training"
            },
            {
                "content": "Building trust with prospects requires active listening, demonstrating expertise, and providing value before asking for commitment.",
                "type": "strategy",
                "source": "sales_methodology"
            }
        ],
        "leadership": [
            {
                "content": "Strategic planning should align short-term actions with long-term vision while remaining adaptable to market changes.",
                "type": "principle",
                "source": "leadership_framework"
            },
            {
                "content": "Effective team development requires clear communication, regular feedback, and empowerment through delegation.",
                "type": "best_practice",
                "source": "management_training"
            }
        ],
        "erp": [
            {
                "content": "Data integrity in ERP systems requires standardized input processes, regular validation, and automated error checking.",
                "type": "technical_requirement",
                "source": "erp_standards"
            }
        ],
        "crm": [
            {
                "content": "Customer satisfaction improves through personalized interactions, timely responses, and proactive problem resolution.",
                "type": "service_standard",
                "source": "customer_service_guide"
            }
        ]
    }
    
    with open(knowledge_dir / "domain_knowledge.json", "w") as f:
        json.dump(domain_knowledge, f, indent=2)
    print("Created domain_knowledge.json")

def list_files_to_remove():
    """List SelfLearningAgent files that can be safely removed after migration"""
    redundant_files = [
        "c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent/src/self_learning_agent.py",
        "c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent/src/knowledge_base_manager.py",
        "c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent/src/vector_db_manager.py",
        "c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent/src/rag_helper.py",
        "c:/Development/ASISaga/RealmOfAgents/SelfLearningAgent/src/agent_Config.py"
    ]
    
    print("\\nFiles that can be removed after migration verification:")
    for file_path in redundant_files:
        if os.path.exists(file_path):
            print(f"- {file_path}")

if __name__ == "__main__":
    print("Starting SelfLearningAgent to AOS migration...")
    
    # Create sample knowledge
    create_sample_knowledge()
    
    # Migrate existing files
    migrate_knowledge_base()
    migrate_config_files()
    
    # List files that can be removed
    list_files_to_remove()
    
    print("\\nMigration complete!")
    print("\\nNext steps:")
    print("1. Test the new AOS learning system")
    print("2. Verify all functionality works correctly")
    print("3. Remove redundant SelfLearningAgent files")
    print("4. Update any imports in other modules")