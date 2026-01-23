"""
RAG (Retrieval-Augmented Generation) Engine for AOS Learning System

Provides vector-based knowledge retrieval capabilities for self-learning agents.
Integrates with ChromaDB or other vector databases for semantic search.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

try:
    from chromadb import Client as ChromaClient
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    ChromaClient = None


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for semantic knowledge retrieval.
    Provides vector-based search capabilities for contextual information.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("AOS.Learning.RAGEngine")

        # Vector database client
        self.vector_client = None
        self.collections = {}

        # Configuration
        self.vector_db_host = self.config.get("vector_db_host", "localhost")
        self.vector_db_port = self.config.get("vector_db_port", 8000)
        self.top_k_default = self.config.get("top_k_snippets", 5)
        self.min_similarity = self.config.get("min_similarity", 0.7)

    async def initialize(self):
        """Initialize the RAG engine and vector database connection"""
        if not CHROMADB_AVAILABLE:
            self.logger.warning("ChromaDB not available - RAG functionality disabled")
            return False

        try:
            # Initialize ChromaDB client
            self.vector_client = ChromaClient(
                Settings(
                    chroma_server_host=self.vector_db_host,
                    chroma_server_http_port=str(self.vector_db_port)
                )
            )

            # Initialize default collections for each domain
            await self._initialize_collections()

            self.logger.info("RAG Engine initialized successfully")
            return True

        except Exception as error:
            self.logger.warning("Failed to initialize RAG Engine: %s", str(error))
            return False

    async def _initialize_collections(self):
        """Initialize vector collections for different domains"""
        default_domains = ["sales", "leadership", "erp", "crm", "general", "interactions"]

        for domain in default_domains:
            try:
                collection_name = f"{domain}_knowledge"

                # Get or create collection
                try:
                    collection = self.vector_client.get_collection(collection_name)
                    self.logger.debug("Retrieved existing collection: %s", collection_name)
                except:
                    collection = self.vector_client.create_collection(
                        name=collection_name,
                        metadata={"domain": domain, "created_at": datetime.utcnow().isoformat()}
                    )
                    self.logger.info("Created new collection: %s", collection_name)

                self.collections[domain] = collection

            except Exception as error:
                self.logger.warning("Failed to initialize collection for %s: %s", domain, str(error))

    async def add_knowledge_entry(self, domain: str, entry_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a knowledge entry to the vector database"""
        if not self.vector_client or domain not in self.collections:
            return False

        try:
            collection = self.collections[domain]

            # Prepare metadata
            entry_metadata = {
                "domain": domain,
                "entry_id": entry_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            if metadata:
                entry_metadata.update(metadata)

            # Add to collection
            collection.add(
                documents=[content],
                metadatas=[entry_metadata],
                ids=[f"{domain}_{entry_id}_{datetime.utcnow().timestamp()}"]
            )

            self.logger.debug("Added knowledge entry to %s: %s", domain, entry_id)
            return True

        except Exception as error:
            self.logger.error("Failed to add knowledge entry: %s", str(error))
            return False

    async def query_knowledge(self, domain: str, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Query knowledge for a specific domain"""
        if not self.vector_client or domain not in self.collections:
            return []

        top_k = top_k or self.top_k_default

        try:
            collection = self.collections[domain]

            # Perform semantic search
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # Process results
            knowledge_entries = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Convert distance to similarity score (assuming cosine distance)
                similarity = 1 - distance

                if similarity >= self.min_similarity:
                    knowledge_entries.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "rank": i + 1
                    })

            self.logger.debug("Retrieved %s relevant entries for %s", len(knowledge_entries), domain)
            return knowledge_entries

        except Exception as error:
            self.logger.error("Failed to query knowledge for %s: %s", domain, str(error))
            return []

    async def query_cross_domain(self, query: str, domains: List[str] = None, top_k: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """Query knowledge across multiple domains"""
        domains = domains or list(self.collections.keys())
        top_k = top_k or self.top_k_default

        results = {}

        for domain in domains:
            domain_results = await self.query_knowledge(domain, query, top_k)
            if domain_results:
                results[domain] = domain_results

        self.logger.debug("Cross-domain query returned results for %s domains", len(results))
        return results

    async def add_interaction_learning(self, user_input: str, response: str, domain: str,
                                     rating: float = None, context: Dict[str, Any] = None):
        """Add interaction data for learning purposes"""
        interaction_content = f"User: {user_input}\nResponse: {response}"

        metadata = {
            "type": "interaction",
            "domain": domain,
            "rating": rating,
            "context": context or {}
        }

        entry_id = f"interaction_{datetime.utcnow().timestamp()}"

        # Add to interactions collection
        await self.add_knowledge_entry("interactions", entry_id, interaction_content, metadata)

        # Also add to domain-specific collection if rating is good
        if rating and rating >= 4.0:
            await self.add_knowledge_entry(domain, entry_id, interaction_content, metadata)

    async def get_similar_interactions(self, query: str, domain: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get similar past interactions for learning"""
        if domain:
            # Query specific domain
            return await self.query_knowledge(domain, query, top_k)
        else:
            # Query interactions collection
            return await self.query_knowledge("interactions", query, top_k)

    async def update_knowledge_quality(self, entry_id: str, domain: str, quality_score: float, feedback: str = None):
        """Update the quality score of a knowledge entry (for future filtering)"""
        # This would typically involve updating metadata in the vector database
        # ChromaDB doesn't support direct updates, so we'd need to track this separately
        self.logger.debug("Quality update for %s/%s: %s", domain, entry_id, quality_score)

        # In a real implementation, you might:
        # 1. Store quality scores in a separate database
        # 2. Re-embed the entry with updated metadata
        # 3. Use the scores for result ranking

    async def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a domain's knowledge base"""
        if not self.vector_client or domain not in self.collections:
            return {}

        try:
            collection = self.collections[domain]
            count = collection.count()

            return {
                "domain": domain,
                "total_entries": count,
                "collection_name": f"{domain}_knowledge",
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as error:
            self.logger.error("Failed to get statistics for %s: %s", domain, str(error))
            return {}

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall RAG system statistics"""
        stats = {
            "vector_db_available": self.vector_client is not None,
            "domains": list(self.collections.keys()),
            "total_collections": len(self.collections),
            "configuration": {
                "host": self.vector_db_host,
                "port": self.vector_db_port,
                "top_k_default": self.top_k_default,
                "min_similarity": self.min_similarity
            }
        }

        # Add per-domain statistics
        domain_stats = {}
        for domain in self.collections.keys():
            domain_stats[domain] = await self.get_domain_statistics(domain)

        stats["domain_statistics"] = domain_stats
        return stats

    async def cleanup(self):
        """Cleanup RAG engine resources"""
        if self.vector_client:
            try:
                # ChromaDB client doesn't require explicit cleanup
                self.logger.info("RAG Engine cleaned up")
            except Exception as error:
                self.logger.error("Error during RAG cleanup: %s", str(error))
