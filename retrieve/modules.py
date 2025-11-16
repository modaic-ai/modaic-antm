import dspy
from retrieve.utils import search_table, search_multiple_tables, hybrid_search
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

lm = dspy.LM(
    model="openrouter/openai/gpt-5",
    temperature=0.7,
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)

dspy.configure(lm=lm)


# ============================================================================
# Structured Data Query Module
# ============================================================================


class DataQuerySignature(dspy.Signature):
    """Generate SQL/pandas query to answer retail analytics questions."""

    question = dspy.InputField(desc="The business question to answer")
    schema_info = dspy.InputField(
        desc="Information about available data tables and columns"
    )
    query_approach = dspy.OutputField(
        desc="Step-by-step approach to answer the question"
    )
    relevant_tables = dspy.OutputField(desc="Comma-separated list of tables needed")
    answer = dspy.OutputField(
        desc="The specific answer to the question with supporting data"
    )


class StructuredDataAnalyzer(dspy.Module):
    """Analyzes structured parquet data to answer quantitative questions."""

    def __init__(self, data_path: str = "dataset/data"):
        super().__init__()
        self.data_path = Path(data_path)
        self.query_generator = dspy.ChainOfThought(DataQuerySignature)
        self._load_schema_info()

    def _load_schema_info(self):
        """Load schema information from parquet files."""
        schema_parts = []
        parquet_files = list(self.data_path.glob("*.parquet"))

        for pq_file in parquet_files[:5]:  # Sample first 5 for speed
            try:
                df = pd.read_parquet(pq_file)
                table_name = pq_file.stem
                columns = ", ".join(df.columns.tolist()[:10])  # First 10 columns
                schema_parts.append(f"{table_name}: {columns}")
            except:
                continue

        self.schema_info = "\n".join(schema_parts)

    def forward(self, question: str) -> dspy.Prediction:
        """Generate analysis for structured data questions."""
        return self.query_generator(question=question, schema_info=self.schema_info)


# ============================================================================
# Document Retrieval Module
# ============================================================================


class DocumentRetrievalSignature(dspy.Signature):
    """Extract relevant information from documents to answer questions."""

    context = dspy.InputField(desc="Retrieved documents from the knowledge base")
    question = dspy.InputField(desc="The question to answer")
    relevant_info = dspy.OutputField(
        desc="Key information from documents relevant to the question"
    )
    answer = dspy.OutputField(desc="Answer derived from the documents")


class SmartDocumentRetriever(dspy.Module):
    """Intelligently retrieves documents based on question analysis."""

    def __init__(self, num_docs: int = 5, tables: Optional[List[str]] = None):
        super().__init__()
        self.num_docs = num_docs
        self.tables = tables or [
            "annual_reports",
            "quarterly_reports",
            "store_reports",
            "inventory_receiving",
            "purchase_orders",
        ]
        self.responder = dspy.ChainOfThought(DocumentRetrievalSignature)

    def _determine_relevant_tables(self, question: str) -> List[str]:
        """Determine which document types are relevant to the question."""
        question_lower = question.lower()

        # Map keywords to table types
        table_mapping = {
            "annual": ["annual_reports"],
            "yearly": ["annual_reports"],
            "quarter": ["quarterly_reports"],
            "q1|q2|q3|q4": ["quarterly_reports"],
            "store": ["store_reports", "sales_receipts"],
            "warehouse": ["warehouse_picking_slips", "inventory_receiving"],
            "inventory": ["inventory_receiving", "warehouse_picking_slips"],
            "purchase order": ["purchase_orders"],
            "promotion|flyer": ["promotional_flyers"],
            "product|catalog": ["product_catalogs"],
            "shipping|manifest": ["shipping_manifests"],
        }

        relevant = []
        for keyword, tables in table_mapping.items():
            if any(kw in question_lower for kw in keyword.split("|")):
                relevant.extend(tables)

        # Default to most comprehensive tables if nothing specific found
        if not relevant:
            relevant = ["annual_reports", "quarterly_reports", "store_reports"]

        # Filter to only available tables
        return [t for t in relevant if t in self.tables][:3]  # Max 3 table types

    def forward(self, question: str) -> dspy.Prediction:
        """Retrieve and analyze documents for the question."""
        # Determine relevant tables
        relevant_tables = self._determine_relevant_tables(question)

        # Extract key terms for hybrid search
        keywords = self._extract_keywords(question)

        # Retrieve documents using hybrid search
        if len(relevant_tables) == 1:
            context = hybrid_search(
                table_names=relevant_tables[0],
                query=question,
                k=self.num_docs,
                keyword_boost_terms=keywords,
                return_type="content",
                include_distance=False,
            )
        else:
            context = search_multiple_tables(
                table_names=relevant_tables,
                query=question,
                k_per_table=max(2, self.num_docs // len(relevant_tables)),
                total_k=self.num_docs,
                merge_strategy="best",
                return_type="content",
                include_distance=False,
            )

        # Analyze documents
        return self.responder(context=context, question=question)

    def _extract_keywords(self, question: str) -> List[str]:
        """Extract important keywords from question for boosting."""
        # Extract years
        import re

        keywords = []

        # Years (2018-2024)
        years = re.findall(r"\b20[12][0-9]\b", question)
        keywords.extend(years)

        # Months
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        for month in months:
            if month in question.lower():
                keywords.append(month)

        # Quarter mentions
        quarters = re.findall(r"\bQ[1-4]\b", question, re.IGNORECASE)
        keywords.extend(quarters)

        # Store/warehouse numbers
        stores = re.findall(r"[Ss]tore\s*#?(\d+)", question)
        warehouses = re.findall(r"[Ww]arehouse\s*#?(\d+)", question)
        keywords.extend([f"Store {s}" for s in stores])
        keywords.extend([f"Warehouse {w}" for w in warehouses])

        return keywords


# ============================================================================
# Hybrid RAG Pipeline
# ============================================================================


class HybridRAGSignature(dspy.Signature):
    """Synthesize answer from both structured data and documents."""

    question = dspy.InputField(desc="The retail analytics question")
    structured_analysis = dspy.InputField(desc="Analysis from structured data")
    document_insights = dspy.InputField(desc="Insights from documents")
    final_answer = dspy.OutputField(desc="Comprehensive answer combining both sources")
    confidence = dspy.OutputField(desc="Confidence level: high/medium/low")


class RetailAnalyticsRAG(dspy.Module):
    """
    Hybrid RAG system for retail analytics that combines:
    1. Structured data analysis (parquet files)
    2. Document retrieval (PDFs)
    3. Intelligent synthesis
    """

    def __init__(
        self,
        num_docs: int = 5,
        use_structured: bool = True,
        use_documents: bool = True,
        data_path: str = "dataset/data",
    ):
        super().__init__()
        self.num_docs = num_docs
        self.use_structured = use_structured
        self.use_documents = use_documents

        # Initialize sub-modules
        if use_structured:
            self.structured_analyzer = StructuredDataAnalyzer(data_path=data_path)

        if use_documents:
            self.doc_retriever = SmartDocumentRetriever(num_docs=num_docs)

        self.synthesizer = dspy.ChainOfThought(HybridRAGSignature)

    def _classify_question(self, question: str) -> str:
        """Classify question type to determine which data sources to use."""
        question_lower = question.lower()

        # Indicators for structured data
        structured_indicators = [
            "how many",
            "how much",
            "total",
            "calculate",
            "count",
            "highest",
            "lowest",
            "average",
            "sum",
            "percentage",
            "which product",
            "which store",
            "which customer",
            "revenue",
            "profit",
            "sales",
            "quantity",
        ]

        # Indicators for documents
        document_indicators = [
            "policy",
            "compliance",
            "audit",
            "approval",
            "signature",
            "report",
            "summary",
            "overview",
            "highlights",
            "why",
            "explain",
            "describe",
            "context",
        ]

        structured_score = sum(
            1 for ind in structured_indicators if ind in question_lower
        )
        document_score = sum(1 for ind in document_indicators if ind in question_lower)

        if structured_score > document_score * 2:
            return "structured"
        elif document_score > structured_score * 2:
            return "documents"
        else:
            return "hybrid"

    def forward(self, question: str) -> dspy.Prediction:
        """Process question through hybrid RAG pipeline."""

        # Classify question
        question_type = self._classify_question(question)

        # Get structured analysis if needed
        if self.use_structured and question_type in ["structured", "hybrid"]:
            structured_result = self.structured_analyzer(question=question)
            structured_analysis = f"Analysis: {structured_result.answer}\nApproach: {structured_result.query_approach}"
        else:
            structured_analysis = "Not applicable for this question type."

        # Get document insights if needed
        if self.use_documents and question_type in ["documents", "hybrid"]:
            doc_result = self.doc_retriever(question=question)
            document_insights = f"Relevant Info: {doc_result.relevant_info}\nDocument Answer: {doc_result.answer}"
        else:
            document_insights = "Not applicable for this question type."

        # Synthesize final answer
        final_result = self.synthesizer(
            question=question,
            structured_analysis=structured_analysis,
            document_insights=document_insights,
        )

        return final_result


# ============================================================================
# Simplified RAG for Quick Testing
# ============================================================================


class SimpleRAG(dspy.Module):
    """Simple RAG for basic document Q&A."""

    def __init__(self, num_docs: int = 5, table_name: str = "annual_reports"):
        super().__init__()
        self.num_docs = num_docs
        self.table_name = table_name
        self.respond = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question: str) -> dspy.Prediction:
        """Simple document retrieval and response."""
        context = search_table(
            table_name=self.table_name,
            query=question,
            k=self.num_docs,
            return_type="content",
        )
        return self.respond(context=context, question=question)
