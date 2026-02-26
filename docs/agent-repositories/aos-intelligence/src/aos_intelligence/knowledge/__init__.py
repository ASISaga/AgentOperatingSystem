"""
Knowledge services for AgentOperatingSystem

Evidence retrieval, indexing contracts, and precedent query system
as specified in features.md.
"""

from .evidence import EvidenceRetrieval, Evidence, EvidenceType
from .indexing import IndexingEngine, IndexedDocument, SearchQuery
from .precedent import PrecedentEngine, PrecedentQuery, PrecedentMatch

__all__ = [
    'EvidenceRetrieval',
    'Evidence',
    'EvidenceType',
    'IndexingEngine',
    'IndexedDocument',
    'SearchQuery',
    'PrecedentEngine',
    'PrecedentQuery',
    'PrecedentMatch'
]
