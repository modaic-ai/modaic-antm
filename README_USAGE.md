# Retail Analytics Question Answering System - Usage Guide

## Overview

This system provides a comprehensive pipeline for answering retail analytics questions using:
1. **Document Ingestion**: PDFs → Embeddings → LanceDB
2. **Retrieval Utilities**: Flexible search across document tables
3. **RAG Pipeline**: Hybrid system combining documents + structured data
4. **Question Answering Interface**: Round-based Q&A with CSV submission generation

## Quick Start

### 1. Ingest Documents (One-time Setup)

```bash
# Ingest all PDF documents into LanceDB (this takes time!)
uv run python -m embed.ingest_data

# Or ingest specific tables only
uv run python -m embed.ingest_data --table annual_reports --max-files 10

# Or test with a small sample first
uv run python -m embed.ingest_data --table annual_reports --max-files 5 --batch-size 2
```

### 2. Answer Questions

#### Manual Mode (No RAG)
```bash
# Process training questions manually
uv run python main.py --round training-questions --rag-type none

# Process specific question range
uv run python main.py --round training-questions --rag-type none --start 0 --end 3
```

#### With Simple RAG (Document-only)
```bash
# Use simple document retrieval
uv run python main.py --round training-questions --rag-type simple --num-docs 5

# Process round-1 questions
uv run python main.py --round round-1-questions --rag-type simple
```

#### With Hybrid RAG (Documents + Structured Data)
```bash
# Use full hybrid system (requires proper LLM configuration)
uv run python main.py --round training-questions --rag-type hybrid --num-docs 5
```

## System Components

### 1. Document Ingestion (`embed/ingest_data.py`)

Processes PDFs and stores them in LanceDB with embeddings.

**Features:**
- Converts PDFs to markdown
- Creates OpenAI embeddings (text-embedding-3-large)
- Stores in separate LanceDB tables by document type
- Batch processing with progress bars

**Available Tables:**
- `annual_reports` (6 PDFs)
- `quarterly_reports` (24 PDFs)
- `store_reports` (36 PDFs)
- `inventory_receiving` (2,191 PDFs)
- `purchase_orders` (2,191 PDFs)
- `promotional_flyers` (119 PDFs)
- `product_catalogs` (24 PDFs)
- `sales_receipts` (65,644 PDFs)
- `shipping_manifests` (13,340 PDFs)
- `warehouse_picking_slips` (13,641 PDFs)

**Total:** ~97,000 PDFs

### 2. Retrieval Utilities (`retrieve/utils.py`)

Flexible document retrieval functions for RAG.

**Key Functions:**

```python
from retrieve.utils import search_table, search_multiple_tables, hybrid_search

# Simple search
results = search_table(
    table_name="annual_reports",
    query="revenue growth 2022",
    k=5,
    return_type="content"  # "content", "dict", or "list"
)

# Multi-table search
results = search_multiple_tables(
    table_names=["annual_reports", "quarterly_reports"],
    query="Q4 performance",
    k_per_table=3,
    merge_strategy="best"  # "concatenate", "interleave", "best"
)

# Hybrid search (semantic + keywords)
results = hybrid_search(
    table_names="annual_reports",
    query="financial performance",
    keyword_boost_terms=["revenue", "profit", "2022"],
    semantic_weight=0.7
)
```

### 3. RAG Modules (`retrieve/modules.py`)

DSPy-based RAG implementations.

**Available Modules:**

1. **SimpleRAG** - Basic document Q&A
   ```python
   from retrieve.modules import SimpleRAG

   rag = SimpleRAG(num_docs=5, table_name="annual_reports")
   result = rag(question="What was the revenue in 2022?")
   print(result.answer)
   ```

2. **SmartDocumentRetriever** - Intelligent multi-table retrieval
   - Automatically selects relevant document types
   - Extracts keywords (years, months, store numbers)
   - Uses hybrid search for better results

3. **StructuredDataAnalyzer** - Parquet data analysis
   - Generates SQL/pandas query approaches
   - Analyzes structured retail data
   - Provides schema-aware answers

4. **RetailAnalyticsRAG** - Full hybrid system
   - Combines documents + structured data
   - Question classification (structured/documents/hybrid)
   - Multi-stage synthesis

### 4. Question Answering Interface (`main.py`)

Interactive system for processing question rounds.

**Features:**
- Parses question markdown files
- Extracts answer schemas automatically
- Supports manual, simple, or hybrid RAG modes
- Generates CSV in correct submission format
- Auto-saves after each question
- Resumable (loads existing answers)

**CSV Output Format:**
```csv
row_index,col_1,col_2,col_3,col_4,col_5
0,3,Electronics,-17958.17,,
1,CA,Jewelry,2500,691182.47,
2,2,45770.69,,
```

## Usage Examples

### Example 1: Manual Entry for Training Questions

```bash
uv run python main.py --round training-questions --rag-type none --start 0 --end 3
```

This will:
1. Load questions 0-2 from `questions/training-questions.md`
2. Show each question and expected schema
3. Prompt for manual entry of values
4. Save to `questions/answers.csv` after each question

### Example 2: RAG-Assisted with Manual Extraction

```bash
uv run python main.py --round training-questions --rag-type simple --num-docs 5
```

This will:
1. Use SimpleRAG to retrieve relevant documents
2. Generate LLM answer
3. Display answer to user
4. Prompt for manual extraction of structured values
5. Save to CSV

### Example 3: Process Round 1 Questions

```bash
uv run python main.py --round round-1-questions --rag-type simple --output round1_submission.csv
```

### Example 4: Resume from Question 5

```bash
uv run python main.py --round training-questions --rag-type simple --start 5
```

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# LanceDB Cloud
LANCEDB_API_KEY=your_api_key
LANCEDB_REGION=us-west-2
LANCEDB_URI=your_db_uri

# OpenRouter (for LLM)
OPENROUTER_API_KEY=your_openrouter_key

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_key
```

### LLM Configuration

Fix the LLM configuration in `retrieve/modules.py`:

```python
# For OpenAI reasoning models (gpt-5, o1, etc.)
lm = dspy.LM(
    model="openrouter/openai/gpt-5",
    temperature=1.0,  # Required for reasoning models
    max_tokens=16000,  # Required for reasoning models
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)

# For standard models (gpt-4, claude, etc.)
lm = dspy.LM(
    model="openrouter/anthropic/claude-3.5-sonnet",
    temperature=0.7,
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)
```

## Question Schemas

Questions are parsed from markdown files. Each question has a schema defining expected answers.

**Example from training-questions.md:**

```markdown
## the warehouse that causes revenue drops

**Question:** Store #5's November 2022 revenue dropped from $500K in October to $300K...

**Observations:**
```json
{
  "question": "Store #5's November 2022...",
  "warehouse_sk": 3,
  "category": "Electronics",
  "revenue_impact": -17958.17,
  "difficulty": 1
}
```

**Answer schema:** `[warehouse_sk, category, revenue_impact]`
**CSV row:** `0,3,Electronics,-17958.17,,`

## Tips for Best Results

1. **Start Small**: Test with 1-2 questions in manual mode first
2. **Ingest Gradually**: Start with small tables (annual_reports) before ingesting all 97k PDFs
3. **Use Simple RAG First**: Get document retrieval working before trying hybrid
4. **Manual Extraction**: Even with RAG, manually verify and extract structured values
5. **Save Often**: The system auto-saves after each question
6. **Resume Support**: You can stop and restart anytime - it loads existing answers

## Troubleshooting

**Error: "OpenAI's reasoning models require temperature=1.0"**
- Fix LLM configuration in `retrieve/modules.py`
- Use standard models instead of reasoning models

**Error: "Table not found"**
- Run ingestion first: `uv run python -m embed.ingest_data --table <table_name>`

**Slow performance**
- Reduce `--num-docs` (default: 5 → try 3)
- Use `--end` to process smaller batches
- Ingest only needed tables

**Wrong CSV format**
- Values must be in correct order matching schema
- Leave unused columns empty (not null)
- Check `questions/answers.csv` after each save

## Next Steps

1. **Ingest documents** you need for your question round
2. **Test RAG** on a few questions manually
3. **Process full round** with RAG assistance
4. **Verify CSV** format matches submission requirements
5. **Submit** to leaderboard!

Good luck! 🚀
