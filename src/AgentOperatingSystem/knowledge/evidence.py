"""
Evidence retrieval interface for AgentOperatingSystem

Standard API for fetching documents, metrics, prior decisions, and external references.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class EvidenceType(str, Enum):
    """Types of evidence"""
    DOCUMENT = "document"
    METRIC = "metric"
    DECISION = "decision"
    EXTERNAL_REFERENCE = "external_reference"
    AUDIT_LOG = "audit_log"


class Evidence(BaseModel):
    """Individual piece of evidence"""
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType
    title: str
    description: Optional[str] = None
    source: str  # Where this evidence came from
    content: Dict[str, Any] = Field(default_factory=dict)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EvidenceRetrieval:
    """
    Standard interface for evidence retrieval across the platform.
    
    Fetches documents, metrics, prior decisions, and external references
    for decision support and audit.
    """
    
    def __init__(self):
        """Initialize evidence retrieval"""
        self._evidence_store: Dict[str, Evidence] = {}
    
    def add_evidence(
        self,
        evidence_type: EvidenceType,
        title: str,
        source: str,
        content: Dict[str, Any],
        description: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Evidence:
        """
        Add evidence to the store.
        
        Args:
            evidence_type: Type of evidence
            title: Evidence title
            source: Evidence source
            content: Evidence content
            description: Optional description
            url: Optional URL
            tags: Optional tags
            
        Returns:
            Created evidence
        """
        evidence = Evidence(
            evidence_type=evidence_type,
            title=title,
            description=description,
            source=source,
            content=content,
            url=url,
            tags=tags or []
        )
        
        self._evidence_store[evidence.evidence_id] = evidence
        return evidence
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Retrieve evidence by ID"""
        return self._evidence_store.get(evidence_id)
    
    def fetch_documents(
        self,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """
        Fetch document evidence.
        
        Args:
            tags: Filter by tags
            source: Filter by source
            limit: Maximum number to return
            
        Returns:
            List of document evidence
        """
        return self._fetch_by_type(
            EvidenceType.DOCUMENT,
            tags=tags,
            source=source,
            limit=limit
        )
    
    def fetch_metrics(
        self,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """Fetch metric evidence"""
        return self._fetch_by_type(
            EvidenceType.METRIC,
            tags=tags,
            source=source,
            limit=limit
        )
    
    def fetch_prior_decisions(
        self,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """Fetch prior decision evidence"""
        return self._fetch_by_type(
            EvidenceType.DECISION,
            tags=tags,
            limit=limit
        )
    
    def fetch_external_references(
        self,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """Fetch external reference evidence"""
        return self._fetch_by_type(
            EvidenceType.EXTERNAL_REFERENCE,
            tags=tags,
            limit=limit
        )
    
    def _fetch_by_type(
        self,
        evidence_type: EvidenceType,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """Internal method to fetch by type with filters"""
        results = []
        
        for evidence in self._evidence_store.values():
            if evidence.evidence_type != evidence_type:
                continue
            
            if source and evidence.source != source:
                continue
            
            if tags:
                # Must match all tags
                if not all(t in evidence.tags for t in tags):
                    continue
            
            results.append(evidence)
            
            if len(results) >= limit:
                break
        
        return results
    
    def search_evidence(
        self,
        query: str,
        evidence_types: Optional[List[EvidenceType]] = None,
        limit: int = 10
    ) -> List[Evidence]:
        """
        Search evidence by query string.
        
        Args:
            query: Search query
            evidence_types: Optional filter by types
            limit: Maximum results
            
        Returns:
            List of matching evidence
        """
        results = []
        query_lower = query.lower()
        
        for evidence in self._evidence_store.values():
            # Filter by type if specified
            if evidence_types and evidence.evidence_type not in evidence_types:
                continue
            
            # Simple text search in title and description
            if query_lower in evidence.title.lower():
                results.append(evidence)
            elif evidence.description and query_lower in evidence.description.lower():
                results.append(evidence)
            elif any(query_lower in tag.lower() for tag in evidence.tags):
                results.append(evidence)
            
            if len(results) >= limit:
                break
        
        return results
