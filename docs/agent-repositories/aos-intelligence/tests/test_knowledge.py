"""
Tests for the knowledge module: EvidenceRetrieval, IndexingEngine, PrecedentEngine.
"""

import pytest
from aos_intelligence.knowledge.evidence import (
    EvidenceRetrieval, Evidence, EvidenceType
)
from aos_intelligence.knowledge.indexing import (
    IndexingEngine, IndexedDocument, SearchQuery
)
from aos_intelligence.knowledge.precedent import (
    PrecedentEngine, PrecedentQuery, PrecedentMatch
)


class TestEvidence:
    def test_evidence_creation(self):
        evidence = Evidence(
            evidence_type=EvidenceType.DOCUMENT,
            title="Test Evidence",
            source="test_source",
            content={"text": "Contract clause 3.1 requires 30-day notice."},
        )
        assert evidence.source == "test_source"
        assert evidence.evidence_type == EvidenceType.DOCUMENT


class TestEvidenceRetrieval:
    def test_add_and_retrieve_by_type(self):
        retrieval = EvidenceRetrieval()
        retrieval.add_evidence(
            evidence_type=EvidenceType.DOCUMENT,
            title="NDA Clause",
            source="contract_db",
            content={"text": "All NDAs require dual approval."},
        )
        docs = retrieval.fetch_documents(limit=5)
        assert len(docs) == 1

    def test_add_policy_evidence(self):
        retrieval = EvidenceRetrieval()
        ev = retrieval.add_evidence(
            evidence_type=EvidenceType.POLICY,
            title="Approval Policy",
            source="legal_policy",
            content={"text": "Contracts above $50k require legal review."},
        )
        assert ev.evidence_type == EvidenceType.POLICY
        assert ev.title == "Approval Policy"

    def test_search_evidence(self):
        retrieval = EvidenceRetrieval()
        retrieval.add_evidence(
            evidence_type=EvidenceType.DOCUMENT,
            title="Contract Termination",
            source="contract_db",
            content={"text": "90-day notice required for termination."},
            tags=["termination", "contract"],
        )
        results = retrieval.search_evidence("termination")
        assert isinstance(results, list)


class TestIndexingEngine:
    def test_ingest_document(self):
        engine = IndexingEngine()
        doc = engine.ingest(
            title="Q2 Sales Playbook",
            content="Our sales approach focuses on value-based selling.",
            content_type="text",
            source="sales_wiki",
        )
        assert doc.title == "Q2 Sales Playbook"
        assert doc.document_id is not None

    def test_search_returns_results(self):
        engine = IndexingEngine()
        engine.ingest(
            title="Enterprise Sales Guide",
            content="When handling enterprise accounts, focus on ROI demonstrations.",
            content_type="text",
            source="sales_wiki",
            tags=["enterprise", "sales"],
        )
        query = SearchQuery(query_text="enterprise ROI", limit=5)
        results = engine.search(query)
        assert isinstance(results, list)

    def test_get_document(self):
        engine = IndexingEngine()
        doc = engine.ingest(
            title="Finance Policy",
            content="All expenses over $10k require VP approval.",
            content_type="policy",
            source="hr_portal",
        )
        retrieved = engine.get_document(doc.document_id)
        assert retrieved is not None
        assert retrieved.document_id == doc.document_id


class TestPrecedentEngine:
    def test_register_and_find_precedent(self):
        engine = PrecedentEngine()
        engine.register_decision(
            decision_id="prec-001",
            decision_type="vendor_contract",
            title="Approved Salesforce Contract",
            description="Approved new SaaS vendor for $95k annual contract",
            outcome="approved",
            tags=["vendor", "saas", "finance"],
        )
        query = PrecedentQuery(
            keywords=["vendor"],
            decision_type="vendor_contract",
        )
        results = engine.find_precedents(query)
        assert isinstance(results, list)

    def test_find_precedents_returns_list(self):
        engine = PrecedentEngine()
        query = PrecedentQuery(keywords=["vendor", "approval"])
        results = engine.find_precedents(query)
        assert isinstance(results, list)

    def test_multiple_precedents(self):
        engine = PrecedentEngine()
        for i in range(3):
            engine.register_decision(
                decision_id=f"prec-{i:03d}",
                decision_type="procurement",
                title=f"Decision {i}",
                description=f"Procurement decision {i}",
                outcome="approved",
                tags=["procurement"],
            )
        query = PrecedentQuery(keywords=["procurement"])
        results = engine.find_precedents(query)
        assert len(results) >= 1
