"""
Precedent query system for AgentOperatingSystem

Similarity and graph-based traversal for analogous decisions and outcomes.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class PrecedentQuery(BaseModel):
    """Query for finding precedent decisions"""
    decision_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    outcome: Optional[str] = None
    min_similarity: float = 0.5  # Minimum similarity score
    limit: int = 10


class PrecedentMatch(BaseModel):
    """Match result for a precedent query"""
    decision_id: str
    similarity_score: float
    match_reason: str
    decision_data: Dict[str, Any] = Field(default_factory=dict)


class PrecedentEngine:
    """
    Engine for finding precedent decisions using similarity and graph traversal.

    Enables context-aware decision support by surfacing analogous past decisions.
    """

    def __init__(self):
        """Initialize precedent engine"""
        self._decisions: Dict[str, Dict[str, Any]] = {}
        self._decision_graph: Dict[str, List[str]] = {}  # decision_id -> related_decision_ids

    def register_decision(
        self,
        decision_id: str,
        decision_type: str,
        title: str,
        description: str,
        outcome: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a decision for precedent lookup.

        Args:
            decision_id: Unique decision ID
            decision_type: Type of decision
            title: Decision title
            description: Description
            outcome: Decision outcome
            tags: Optional tags
            metadata: Optional metadata
        """
        self._decisions[decision_id] = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "title": title,
            "description": description,
            "outcome": outcome,
            "tags": tags or [],
            "metadata": metadata or {},
            "registered_at": datetime.utcnow().isoformat()
        }

        # Initialize in graph
        if decision_id not in self._decision_graph:
            self._decision_graph[decision_id] = []

    def link_decisions(self, decision_id_1: str, decision_id_2: str):
        """
        Create a link between two related decisions.

        Args:
            decision_id_1: First decision ID
            decision_id_2: Second decision ID
        """
        if decision_id_1 in self._decision_graph:
            if decision_id_2 not in self._decision_graph[decision_id_1]:
                self._decision_graph[decision_id_1].append(decision_id_2)

        if decision_id_2 in self._decision_graph:
            if decision_id_1 not in self._decision_graph[decision_id_2]:
                self._decision_graph[decision_id_2].append(decision_id_1)

    def find_precedents(self, query: PrecedentQuery) -> List[PrecedentMatch]:
        """
        Find precedent decisions matching the query.

        Args:
            query: Precedent query

        Returns:
            List of precedent matches sorted by similarity
        """
        matches = []

        for decision_id, decision_data in self._decisions.items():
            similarity = self._calculate_similarity(decision_data, query)

            if similarity >= query.min_similarity:
                match_reason = self._explain_match(decision_data, query, similarity)
                matches.append(PrecedentMatch(
                    decision_id=decision_id,
                    similarity_score=similarity,
                    match_reason=match_reason,
                    decision_data=decision_data
                ))

        # Sort by similarity score
        matches.sort(key=lambda x: x.similarity_score, reverse=True)

        return matches[:query.limit]

    def find_related_by_graph(
        self,
        decision_id: str,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[str]:
        """
        Find related decisions using graph traversal.

        Args:
            decision_id: Starting decision ID
            max_depth: Maximum depth to traverse
            limit: Maximum results

        Returns:
            List of related decision IDs
        """
        if decision_id not in self._decision_graph:
            return []

        visited = set()
        queue = [(decision_id, 0)]  # (decision_id, depth)
        related = []

        while queue and len(related) < limit:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            if current_id != decision_id:
                related.append(current_id)

            # Add neighbors to queue
            if depth < max_depth:
                for neighbor_id in self._decision_graph.get(current_id, []):
                    if neighbor_id not in visited:
                        queue.append((neighbor_id, depth + 1))

        return related[:limit]

    def _calculate_similarity(
        self,
        decision_data: Dict[str, Any],
        query: PrecedentQuery
    ) -> float:
        """Calculate similarity score between decision and query"""
        score = 0.0
        max_score = 0.0

        # Decision type match (weight: 3)
        max_score += 3.0
        if query.decision_type:
            if decision_data["decision_type"] == query.decision_type:
                score += 3.0
        else:
            score += 1.5  # Partial credit if no type specified

        # Tag overlap (weight: 2)
        if query.tags:
            max_score += 2.0
            decision_tags = set(decision_data.get("tags", []))
            query_tags = set(query.tags)
            overlap = len(decision_tags & query_tags)
            if len(query_tags) > 0:
                score += 2.0 * (overlap / len(query_tags))

        # Keyword match (weight: 2)
        if query.keywords:
            max_score += 2.0
            text = f"{decision_data['title']} {decision_data['description']}".lower()
            matched = sum(1 for kw in query.keywords if kw.lower() in text)
            if len(query.keywords) > 0:
                score += 2.0 * (matched / len(query.keywords))

        # Outcome match (weight: 1)
        max_score += 1.0
        if query.outcome:
            if decision_data.get("outcome") == query.outcome:
                score += 1.0
        else:
            score += 0.5

        # Normalize to 0-1
        return score / max_score if max_score > 0 else 0.0

    def _explain_match(
        self,
        decision_data: Dict[str, Any],
        query: PrecedentQuery,
        similarity: float
    ) -> str:
        """Explain why this decision matches"""
        reasons = []

        if query.decision_type and decision_data["decision_type"] == query.decision_type:
            reasons.append(f"same type ({decision_data['decision_type']})")

        if query.tags:
            decision_tags = set(decision_data.get("tags", []))
            query_tags = set(query.tags)
            common = decision_tags & query_tags
            if common:
                reasons.append(f"common tags: {', '.join(common)}")

        if query.outcome and decision_data.get("outcome") == query.outcome:
            reasons.append(f"same outcome ({decision_data['outcome']})")

        if not reasons:
            reasons.append("general similarity")

        return f"Match (score: {similarity:.2f}): " + "; ".join(reasons)
