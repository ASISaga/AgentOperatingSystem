"""
Indexing contracts for AgentOperatingSystem

Content ingestion, normalization, enrichment, and searchable field definitions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class IndexedDocument(BaseModel):
    """Document that has been indexed"""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    content_type: str  # e.g., "text", "markdown", "json"
    source: str
    indexed_at: datetime = Field(default_factory=datetime.utcnow)

    # Searchable fields
    searchable_fields: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchQuery(BaseModel):
    """Search query specification"""
    query_text: str
    fields: Optional[List[str]] = None  # Fields to search in
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = 10


class IndexingEngine:
    """
    Engine for content ingestion, normalization, and indexing.

    Provides searchable field definitions and full-text search.
    """

    def __init__(self):
        """Initialize indexing engine"""
        self._index: Dict[str, IndexedDocument] = {}
        self._inverted_index: Dict[str, List[str]] = {}  # word -> [doc_ids]

    def ingest(
        self,
        title: str,
        content: str,
        content_type: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> IndexedDocument:
        """
        Ingest and index a document.

        Args:
            title: Document title
            content: Document content
            content_type: Content type
            source: Document source
            metadata: Optional metadata
            tags: Optional tags

        Returns:
            Indexed document
        """
        # Normalize content (simple lowercase for now)
        normalized_content = content.lower()

        # Extract searchable fields
        searchable_fields = self._extract_searchable_fields(
            title, normalized_content, metadata or {}
        )

        doc = IndexedDocument(
            title=title,
            content=content,
            content_type=content_type,
            source=source,
            searchable_fields=searchable_fields,
            metadata=metadata or {},
            tags=tags or []
        )

        # Store in index
        self._index[doc.document_id] = doc

        # Build inverted index
        self._build_inverted_index(doc)

        return doc

    def search(self, query: SearchQuery) -> List[IndexedDocument]:
        """
        Search indexed documents.

        Args:
            query: Search query

        Returns:
            List of matching documents
        """
        query_words = query.query_text.lower().split()

        # Find documents containing query words
        doc_scores: Dict[str, int] = {}

        for word in query_words:
            doc_ids = self._inverted_index.get(word, [])
            for doc_id in doc_ids:
                doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1

        # Sort by score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Apply filters and return results
        results = []
        for doc_id, score in sorted_docs:
            doc = self._index.get(doc_id)
            if not doc:
                continue

            # Apply filters
            if query.filters:
                if not self._matches_filters(doc, query.filters):
                    continue

            results.append(doc)

            if len(results) >= query.limit:
                break

        return results

    def get_document(self, document_id: str) -> Optional[IndexedDocument]:
        """Retrieve a document by ID"""
        return self._index.get(document_id)

    def _extract_searchable_fields(
        self,
        title: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract searchable fields from document"""
        return {
            "title_words": title.lower().split(),
            "content_preview": content[:200],
            "word_count": len(content.split()),
            "has_metadata": len(metadata) > 0
        }

    def _build_inverted_index(self, doc: IndexedDocument):
        """Build inverted index for document"""
        # Index title words
        for word in doc.title.lower().split():
            if word not in self._inverted_index:
                self._inverted_index[word] = []
            if doc.document_id not in self._inverted_index[word]:
                self._inverted_index[word].append(doc.document_id)

        # Index content words
        for word in doc.content.lower().split():
            if word not in self._inverted_index:
                self._inverted_index[word] = []
            if doc.document_id not in self._inverted_index[word]:
                self._inverted_index[word].append(doc.document_id)

        # Index tags
        for tag in doc.tags:
            word = tag.lower()
            if word not in self._inverted_index:
                self._inverted_index[word] = []
            if doc.document_id not in self._inverted_index[word]:
                self._inverted_index[word].append(doc.document_id)

    def _matches_filters(self, doc: IndexedDocument, filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        for key, value in filters.items():
            if key == "source":
                if doc.source != value:
                    return False
            elif key == "content_type":
                if doc.content_type != value:
                    return False
            elif key == "tags":
                # Must have all specified tags
                if not all(tag in doc.tags for tag in value):
                    return False
            elif key in doc.metadata:
                if doc.metadata[key] != value:
                    return False

        return True
