"""Test script for RAG pipeline."""

from retrieve.modules import SimpleRAG, SmartDocumentRetriever, RetailAnalyticsRAG


def test_simple_rag():
    """Test simple RAG with a basic question."""
    print("=" * 80)
    print("TEST 1: Simple RAG (Document-only)")
    print("=" * 80)

    rag = SimpleRAG(num_docs=3, table_name="annual_reports")
    question = "How much did our net profit increase from 2021 to 2022?"

    print(f"\nQuestion: {question}")
    print("\nProcessing...")

    try:
        result = rag(question=question)
        print(f"\nAnswer: {result.answer}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


def test_smart_retriever():
    """Test smart document retriever."""
    print("\n" + "=" * 80)
    print("TEST 2: Smart Document Retriever")
    print("=" * 80)

    retriever = SmartDocumentRetriever(num_docs=3)
    question = "What was our most popular category in 2023?"

    print(f"\nQuestion: {question}")
    print("\nProcessing...")

    try:
        result = retriever(question=question)
        print(f"\nRelevant Info: {result.relevant_info}")
        print(f"\nAnswer: {result.answer}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


def test_hybrid_rag():
    """Test full hybrid RAG pipeline."""
    print("\n" + "=" * 80)
    print("TEST 3: Hybrid RAG (Documents + Structured Data)")
    print("=" * 80)

    # Note: This requires both document and structured data
    rag = RetailAnalyticsRAG(num_docs=3, use_structured=True, use_documents=True)

    question = "In 2022, which store had the highest net profit in sales?"

    print(f"\nQuestion: {question}")
    print("\nProcessing...")

    try:
        result = rag(question=question)
        print(f"\nFinal Answer: {result.final_answer}")
        print(f"Confidence: {result.confidence}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run tests
    test_simple_rag()
    # test_smart_retriever()  # Uncomment when ready
    # test_hybrid_rag()  # Uncomment when ready

    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)
