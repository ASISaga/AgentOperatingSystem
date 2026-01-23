"""
Knowledge services for AgentOperatingSystem

Evidence retrieval, indexing contracts, and precedent query system
as specified in features.md.
"""

from .evidence import Evidence, EvidenceRetrieval, EvidenceType
from .indexing import IndexedDocument, IndexingEngine, SearchQuery
from .precedent import PrecedentEngine, PrecedentMatch, PrecedentQuery

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
