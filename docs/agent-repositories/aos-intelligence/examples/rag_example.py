"""
Example: RAG Engine and Knowledge Retrieval

Demonstrates how to use RAGEngine, IndexingEngine, EvidenceRetrieval,
and PrecedentEngine for knowledge-augmented agent responses.

Prerequisites:
    pip install "aos-intelligence[rag]"   # for RAGEngine (requires chromadb)
    pip install "aos-intelligence"        # for IndexingEngine, Evidence, Precedent
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_rag_engine():
    """Example: RAG-based document retrieval."""
    print("\n" + "=" * 70)
    print("Example 1: RAG Engine")
    print("=" * 70 + "\n")

    from aos_intelligence.learning import RAGEngine

    rag = RAGEngine(config={
        "vector_db_host": "localhost",
        "vector_db_port": 8000,
        "top_k_snippets": 5,
        "min_similarity": 0.7,
    })

    # Initialize — ChromaDB will be used if installed; otherwise skipped
    initialized = await rag.initialize()
    print(f"  RAG Engine initialized: {initialized}")

    if initialized:
        # Index documents by domain
        await rag.add_knowledge_entry(
            domain="sales_playbook",
            entry_id="sp-001",
            content="Our sales methodology focuses on value-based selling and building long-term relationships.",
            metadata={"version": "2025"},
        )
        await rag.add_knowledge_entry(
            domain="sales_playbook",
            entry_id="sp-002",
            content="Enterprise objection handling: always lead with ROI and 3-year TCO analysis.",
            metadata={"category": "objection_handling"},
        )

        # Retrieve relevant context
        results = await rag.query_knowledge(
            domain="sales_playbook",
            query="How should we handle enterprise budget objections?",
        )
        print(f"  Retrieved {len(results)} documents:")
        for r in results:
            print(f"    [{r.get('score', 0):.2f}] {r.get('content', '')[:80]}")
    else:
        print("  ChromaDB not available — install with: pip install chromadb")


async def example_indexing_engine():
    """Example: document indexing and search."""
    print("\n" + "=" * 70)
    print("Example 2: Indexing Engine")
    print("=" * 70 + "\n")

    from aos_intelligence.knowledge import IndexingEngine, IndexedDocument, SearchQuery

    engine = IndexingEngine()

    # Index documents
    for doc_data in [
        ("Expense Policy 2025", "All expenses over $10k require VP approval. Travel must be booked via corporate portal.", "policy", "hr_policies", {"domain": "finance"}),
        ("Vendor Onboarding Policy", "New vendors require legal review and security assessment before contract signing.", "policy", "legal_policies", {"domain": "legal"}),
        ("Enterprise Sales Guide", "Enterprise deals over $500k require executive sponsorship and a dedicated success team.", "guide", "sales_playbook", {"domain": "sales"}),
    ]:
        title, content, content_type, source, metadata = doc_data
        doc = engine.ingest(title=title, content=content, content_type=content_type, source=source, metadata=metadata)
        print(f"  Indexed: {doc.title} (id={doc.document_id})")

    # Search
    query = SearchQuery(query_text="vendor approval process", limit=3)
    results = engine.search(query)
    print(f"\n  Search results for '{query.query_text}':")
    for result in results:
        print(f"    - {result.title}: {result.content[:60]}...")


async def example_precedent_engine():
    """Example: precedent-based decision support."""
    print("\n" + "=" * 70)
    print("Example 3: Precedent Engine")
    print("=" * 70 + "\n")

    from aos_intelligence.knowledge import PrecedentEngine, PrecedentQuery, PrecedentMatch

    engine = PrecedentEngine()

    # Record historical precedents
    precedents_data = [
        ("prec-001", "vendor_contract", "Approved SaaS Vendor (Salesforce)",
         "Approved new SaaS vendor (Salesforce) for $95k annual contract", "approved",
         ["vendor", "saas", "finance"]),
        ("prec-002", "vendor_onboarding", "Rejected Vendor: Security Failure",
         "Rejected vendor due to failed security assessment", "rejected",
         ["vendor", "security", "legal"]),
        ("prec-003", "emergency_procurement", "Emergency Procurement Exception",
         "Approved exception for emergency procurement ($150k) with CEO sign-off", "approved_with_exception",
         ["vendor", "emergency", "finance", "exception"]),
    ]

    for prec_id, decision_type, title, description, outcome, tags in precedents_data:
        engine.register_decision(
            decision_id=prec_id,
            decision_type=decision_type,
            title=title,
            description=description,
            outcome=outcome,
            tags=tags,
        )
        print(f"  Recorded precedent: {prec_id} ({outcome})")

    # Query for relevant precedents
    query = PrecedentQuery(
        keywords=["vendor", "contract"],
        decision_type="vendor_contract",
        outcome="approved",
    )
    results = engine.find_precedents(query)
    print(f"\n  Relevant precedents for new vendor approval:")
    for match in results:
        print(f"    [{match.similarity_score:.0%}] {match.decision_data.get('description', '')[:70]}")


async def example_evidence_retrieval():
    """Example: structured evidence retrieval."""
    print("\n" + "=" * 70)
    print("Example 4: Evidence Retrieval")
    print("=" * 70 + "\n")

    from aos_intelligence.knowledge import EvidenceRetrieval, Evidence, EvidenceType

    retrieval = EvidenceRetrieval()

    # Add evidence
    evidence_items_data = [
        (EvidenceType.DOCUMENT, "MSA Termination Clause", "contract_db",
         {"text": "Master Service Agreement clause 12.3: 90-day termination notice required."}),
        (EvidenceType.POLICY, "Contract Approval Policy", "legal_policy",
         {"text": "All contracts above $50k must be reviewed by Legal before execution."}),
    ]

    for ev_type, title, source, content in evidence_items_data:
        retrieval.add_evidence(evidence_type=ev_type, title=title, source=source, content=content)

    results = retrieval.fetch_documents(limit=5)
    print(f"  Evidence retrieved: {len(results)} items")
    for ev in results:
        text = ev.content.get("text", "") if isinstance(ev.content, dict) else str(ev.content)
        print(f"    [{ev.evidence_type.value}] {text[:70]}")


async def main():
    await example_rag_engine()
    await example_indexing_engine()
    await example_precedent_engine()
    await example_evidence_retrieval()
    print("\nAll examples completed.")


if __name__ == "__main__":
    asyncio.run(main())
