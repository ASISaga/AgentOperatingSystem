"""
Knowledge Manager for AOS Learning System

Manages domain-specific knowledge, contexts, and directives for self-learning agents.
Integrates with the AOS storage system for persistence and provides knowledge retrieval.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..storage.manager import StorageManager


class KnowledgeManager:
    """
    Manages domain knowledge, contexts, and learning directives.
    Provides the foundational knowledge layer for self-learning agents.
    """

    def __init__(self, storage_manager: StorageManager, config: Dict[str, Any] = None):
        self.storage = storage_manager
        self.config = config or {}
        self.logger = logging.getLogger("AOS.Learning.KnowledgeManager")

        # Knowledge repositories
        self.domain_contexts = {}
        self.domain_knowledge = {}
        self.agent_directives = {}
        self.interaction_patterns = {}

        # Default knowledge base path
        self.knowledge_base_path = self.config.get("knowledge_base_path", "knowledge")

    async def initialize(self):
        """Initialize the knowledge manager and load existing knowledge"""
        try:
            await self._load_domain_contexts()
            await self._load_domain_knowledge()
            await self._load_agent_directives()
            await self._load_interaction_patterns()

            self.logger.info("Knowledge Manager initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Knowledge Manager: {e}")
            raise

    async def _load_domain_contexts(self):
        """Load domain contexts from storage"""
        try:
            contexts_path = f"{self.knowledge_base_path}/domain_contexts.json"
            if await self.storage.exists(contexts_path):
                data = await self.storage.read_json(contexts_path)
                self.domain_contexts = data
                self.logger.info(f"Loaded contexts for {len(self.domain_contexts)} domains")
            else:
                # Initialize with default contexts
                self.domain_contexts = self._get_default_contexts()
                await self.storage.write_json(contexts_path, self.domain_contexts)

        except Exception as e:
            self.logger.error(f"Failed to load domain contexts: {e}")

    async def _load_domain_knowledge(self):
        """Load domain knowledge from storage"""
        try:
            knowledge_path = f"{self.knowledge_base_path}/domain_knowledge.json"
            if await self.storage.exists(knowledge_path):
                data = await self.storage.read_json(knowledge_path)
                self.domain_knowledge = data
                self.logger.info(f"Loaded knowledge for {len(self.domain_knowledge)} domains")
            else:
                # Initialize with empty knowledge base
                self.domain_knowledge = {}
                await self.storage.write_json(knowledge_path, self.domain_knowledge)

        except Exception as e:
            self.logger.error(f"Failed to load domain knowledge: {e}")

    async def _load_agent_directives(self):
        """Load agent directives from storage"""
        try:
            directives_path = f"{self.knowledge_base_path}/agent_directives.json"
            if await self.storage.exists(directives_path):
                data = await self.storage.read_json(directives_path)
                self.agent_directives = data
                self.logger.info(f"Loaded directives for {len(self.agent_directives)} domains")
            else:
                # Initialize with default directives
                self.agent_directives = self._get_default_directives()
                await self.storage.write_json(directives_path, self.agent_directives)

        except Exception as e:
            self.logger.error(f"Failed to load agent directives: {e}")

    async def _load_interaction_patterns(self):
        """Load learned interaction patterns from storage"""
        try:
            patterns_path = f"{self.knowledge_base_path}/interaction_patterns.json"
            if await self.storage.exists(patterns_path):
                data = await self.storage.read_json(patterns_path)
                self.interaction_patterns = data
                self.logger.info(f"Loaded {len(self.interaction_patterns)} interaction patterns")
            else:
                self.interaction_patterns = {}
                await self.storage.write_json(patterns_path, self.interaction_patterns)

        except Exception as e:
            self.logger.error(f"Failed to load interaction patterns: {e}")

    def _get_default_contexts(self) -> Dict[str, Any]:
        """Get default domain contexts"""
        return {
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

    def _get_default_directives(self) -> Dict[str, str]:
        """Get default agent directives"""
        return {
            "sales": "Focus on understanding customer needs, building relationships, and presenting value propositions that align with business objectives.",
            "leadership": "Prioritize strategic thinking, team empowerment, and data-driven decision making while maintaining stakeholder alignment.",
            "erp": "Ensure process efficiency, data integrity, and seamless system integration while optimizing business operations.",
            "crm": "Maintain customer-centric approach, ensure data accuracy, and provide exceptional service experiences.",
            "general": "Provide accurate, helpful information while maintaining professionalism and seeking clarity when needed."
        }

    async def get_domain_context(self, domain: str) -> Dict[str, Any]:
        """Get context for a specific domain"""
        return self.domain_contexts.get(domain, self.domain_contexts.get("general", {}))

    async def get_domain_knowledge(self, domain: str) -> List[Dict[str, Any]]:
        """Get knowledge entries for a specific domain"""
        return self.domain_knowledge.get(domain, [])

    async def get_agent_directives(self, domain: str) -> str:
        """Get directives for a specific domain"""
        return self.agent_directives.get(domain, self.agent_directives.get("general", ""))

    async def add_knowledge_entry(self, domain: str, entry: Dict[str, Any]):
        """Add a new knowledge entry to a domain"""
        if domain not in self.domain_knowledge:
            self.domain_knowledge[domain] = []

        entry["timestamp"] = datetime.utcnow().isoformat()
        entry["source"] = "learning"

        self.domain_knowledge[domain].append(entry)

        # Persist to storage
        knowledge_path = f"{self.knowledge_base_path}/domain_knowledge.json"
        await self.storage.write_json(knowledge_path, self.domain_knowledge)

        self.logger.info(f"Added knowledge entry to domain: {domain}")

    async def update_interaction_pattern(self, pattern_id: str, pattern: Dict[str, Any]):
        """Update or add an interaction pattern"""
        pattern["last_updated"] = datetime.utcnow().isoformat()
        self.interaction_patterns[pattern_id] = pattern

        # Persist to storage
        patterns_path = f"{self.knowledge_base_path}/interaction_patterns.json"
        await self.storage.write_json(patterns_path, self.interaction_patterns)

        self.logger.debug(f"Updated interaction pattern: {pattern_id}")

    async def get_interaction_patterns(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get interaction patterns with optional filtering"""
        patterns = list(self.interaction_patterns.values())

        if filter_criteria:
            # Apply filtering logic here
            filtered_patterns = []
            for pattern in patterns:
                matches = True
                for key, value in filter_criteria.items():
                    if key in pattern and pattern[key] != value:
                        matches = False
                        break
                if matches:
                    filtered_patterns.append(pattern)
            return filtered_patterns

        return patterns

    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of the knowledge base"""
        return {
            "domains": list(self.domain_contexts.keys()),
            "knowledge_entries": sum(len(entries) for entries in self.domain_knowledge.values()),
            "interaction_patterns": len(self.interaction_patterns),
            "last_updated": datetime.utcnow().isoformat()
        }