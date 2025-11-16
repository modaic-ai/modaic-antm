# Retail Analytics RAG System - Complete Summary

## ✅ What's Been Built

A complete end-to-end RAG system for answering retail analytics questions with automatic CSV submission generation.

## 📁 Project Structure

```
modaic-antm/
├── db/
│   └── lancedb.py              # LanceDB connection configuration
├── embed/
│   ├── utils.py                # PDF→markdown + embedding utilities
│   └── ingest_data.py          # Document ingestion pipeline ⭐
├── retrieve/
│   ├── utils.py                # Flexible retrieval functions ⭐
│   └── modules.py              # DSPy RAG modules ⭐
├── questions/
│   ├── training-questions.md   # Round 1 questions (10 questions)
│   ├── round-1-questions.md    # Round 2 questions (20 questions)
│   └── answers.csv             # Submission output
├── dataset/
│   ├── data/                   # Structured parquet files
│   │   ├── store_sales.parquet
│   │   ├── customer.parquet
│   │   ├── inventory.parquet
│   │   └── ... (16 total)
│   └── [document_type]/pdf/    # ~97,000 PDF documents
├── main.py                     # Question answering interface ⭐
├── test_rag.py                 # RAG testing script
├── README_USAGE.md             # Complete usage guide
└── SYSTEM_SUMMARY.md           # This file
```

## 🚀 Complete Pipeline

### 1️⃣ Document Ingestion Pipeline (`embed/ingest_data.py`)

**What it does:**
- Processes PDFs from `dataset/[table_name]/pdf/` directories
- Converts PDFs to markdown using MarkItDown
- Creates embeddings using OpenAI text-embedding-3-large
- Stores in separate LanceDB tables with vector search

**Usage:**
```bash
# Ingest all documents (WARNING: 97k PDFs, takes hours!)
uv run python -m embed.ingest_data

# Ingest specific table
uv run python -m embed.ingest_data --table annual_reports

# Test with limited files
uv run python -m embed.ingest_data --table annual_reports --max-files 10 --batch-size 5
```

**Available Document Tables:**
| Table | PDF Count | Description |
|-------|-----------|-------------|
| annual_reports | 6 | Annual financial reports |
| quarterly_reports | 24 | Quarterly reports |
| store_reports | 36 | Store performance reports |
| inventory_receiving | 2,191 | Warehouse receiving docs |
| purchase_orders | 2,191 | Purchase order documents |
| promotional_flyers | 119 | Marketing materials |
| product_catalogs | 24 | Product catalogs |
| sales_receipts | 65,644 | Individual sales receipts |
| shipping_manifests | 13,340 | Shipping documentation |
| warehouse_picking_slips | 13,641 | Warehouse picking docs |

**Total:** ~97,000 PDFs

### 2️⃣ Retrieval Utilities (`retrieve/utils.py`)

**What it provides:**
- `list_tables()` - List available document tables
- `get_table_info(table_name)` - Get table metadata
- `search_table(...)` - Search single table with vector similarity
- `search_multiple_tables(...)` - Search across multiple tables with merge strategies
- `hybrid_search(...)` - Combine semantic + keyword search
- `get_documents_by_filename(...)` - Filter by filename pattern

**Key Features:**
- 3 return formats: "content" (for LLMs), "dict" (for inspection), "list" (for processing)
- Distance thresholding
- SQL-like prefilters
- Merge strategies: concatenate, interleave, best
- Keyword boosting for hybrid search

**Example:**
```python
from retrieve.utils import search_table, hybrid_search

# Simple search
context = search_table(
    table_name="annual_reports",
    query="revenue growth 2022",
    k=5,
    return_type="content"
)

# Hybrid search with keyword boosting
results = hybrid_search(
    table_names="annual_reports",
    query="financial performance",
    keyword_boost_terms=["revenue", "profit", "2022"],
    semantic_weight=0.7,
    k=5
)
```

### 3️⃣ RAG Modules (`retrieve/modules.py`)

**What it provides:**

1. **SimpleRAG** - Basic document Q&A
   - Single table retrieval
   - Chain-of-thought reasoning
   - Good for document-only questions

2. **SmartDocumentRetriever** - Intelligent retrieval
   - Auto-selects relevant document types
   - Extracts keywords (years, months, store #s)
   - Hybrid search with boosting

3. **StructuredDataAnalyzer** - Parquet data analysis
   - Loads schema from parquet files
   - Generates query approaches
   - Good for quantitative questions

4. **RetailAnalyticsRAG** - Full hybrid system
   - Combines documents + structured data
   - Question classification (structured/documents/hybrid)
   - Multi-stage synthesis with confidence scores

**Architecture:**
```
Question → Classify → [ Structured Analysis ]
                   → [ Document Retrieval  ] → Synthesize → Answer
                                            → Confidence
```

**Example:**
```python
from retrieve.modules import RetailAnalyticsRAG

rag = RetailAnalyticsRAG(
    num_docs=5,
    use_structured=True,
    use_documents=True
)

result = rag(question="In 2022, which store had the highest net profit?")
print(f"Answer: {result.final_answer}")
print(f"Confidence: {result.confidence}")
```

### 4️⃣ Question Answering Interface (`main.py`)

**What it does:**
- Parses question markdown files
- Extracts answer schemas automatically
- Processes questions in rounds
- Supports 3 modes: manual, simple RAG, hybrid RAG
- Generates CSV in correct submission format
- Auto-saves after each question
- Resumable (loads existing answers)

**Usage:**

```bash
# Manual mode (no RAG)
uv run python main.py --round training-questions --rag-type none

# Simple RAG mode
uv run python main.py --round training-questions --rag-type simple --num-docs 5

# Hybrid RAG mode (documents + structured data)
uv run python main.py --round training-questions --rag-type hybrid

# Process specific question range
uv run python main.py --round training-questions --rag-type simple --start 0 --end 3

# Custom output file
uv run python main.py --round round-1-questions --output round1_answers.csv
```

**Interactive Workflow:**
1. Displays question text
2. Shows expected answer schema
3. (If RAG enabled) Retrieves context and generates answer
4. Prompts for manual extraction of structured values
5. Saves to CSV in correct format
6. Asks to continue to next question

**Output Format:**
```csv
row_index,col_1,col_2,col_3,col_4,col_5
0,3,Electronics,-17958.17,,
1,CA,Jewelry,2500,691182.47,
2,2,45770.69,,,
```

## 📊 Data Sources

### Structured Data (Parquet Files)
Located in `dataset/data/`:
- `store_sales.parquet` (18M) - Store sales transactions
- `web_sales.parquet` (4.6M) - Web sales
- `catalog_sales.parquet` (13M) - Catalog sales
- `store_returns.parquet` (4M) - Returns data
- `inventory.parquet` (913K) - Inventory levels
- `customer.parquet` (2.6M) - Customer data
- `item.parquet` (411K) - Product catalog
- `store.parquet` (11K) - Store metadata
- `warehouse.parquet` (5.4K) - Warehouse info
- Plus demographics, dates, promotions, etc.

### Document Data (PDFs)
- 10 document types across ~97,000 PDF files
- Reports: annual, quarterly, store-level
- Operations: inventory, purchase orders, shipping
- Sales: receipts, promotional flyers
- Logistics: warehouse picking slips, manifests

## 🎯 Question Types

The system handles 30 questions across 2 rounds:

**Round 1 (Training Questions):** 10 questions
- Revenue analysis
- Inventory issues
- Returns analysis
- Product performance
- Year-over-year comparisons

**Round 2:** 20 questions
- Complex analytics (ROI, fraud detection)
- Operational issues (compliance, damage rates)
- Customer behavior analysis
- Seasonal patterns
- Promotional effectiveness

**Answer Types:**
- Numeric: integers, floats (revenue, counts, percentages)
- Categorical: strings (store names, categories, states)
- Identifiers: SKUs, customer IDs, ticket numbers
- Multiple values per question (1-5 columns)

## ⚙️ Configuration

### Required Environment Variables (`.env`)
```env
# LanceDB Cloud
LANCEDB_API_KEY=your_api_key
LANCEDB_REGION=us-west-2
LANCEDB_URI=your_db_uri

# OpenRouter (for LLM)
OPENROUTER_API_KEY=your_key

# OpenAI (for embeddings)
OPENAI_API_KEY=your_key
```

### LLM Model Selection
Edit `retrieve/modules.py`:

```python
# Current: Claude 3.5 Sonnet (recommended)
lm = dspy.LM(
    model="openrouter/anthropic/claude-3.5-sonnet",
    temperature=0.7,
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)

# Alternative: GPT-4
lm = dspy.LM(
    model="openrouter/openai/gpt-4-turbo",
    temperature=0.7,
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)

# For reasoning models (gpt-5, o1):
lm = dspy.LM(
    model="openrouter/openai/gpt-5",
    temperature=1.0,  # Required!
    max_tokens=16000,  # Required!
    api_base=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY,
)
```

## 🧪 Testing

### Test Document Retrieval
```bash
uv run python -c "
from retrieve.utils import list_tables, search_table

tables = list_tables()
print(f'Available tables: {tables}')

results = search_table('annual_reports', 'revenue 2022', k=2, return_type='dict', include_distance=True)
for r in results:
    print(f'{r[\"filename\"]}: {r[\"_distance\"]:.4f}')
"
```

### Test RAG Modules
```bash
# SimpleRAG test
uv run python test_rag.py

# Or test directly
uv run python -c "
from retrieve.modules import SimpleRAG

rag = SimpleRAG(num_docs=3)
result = rag(question='What was the profit in 2022?')
print(result.answer)
"
```

### Test Question Parsing
```bash
uv run python -c "
from main import QuestionRound
from pathlib import Path

round_obj = QuestionRound(Path('questions/training-questions.md'))
print(f'Questions: {len(round_obj.questions)}')
print(f'Q1 schema: {round_obj.get_answer_schema(0)}')
"
```

## 📝 Workflow Recommendations

### First Time Setup
1. **Test retrieval** on ingested documents (annual_reports already has 6 docs)
2. **Run 1 question** in manual mode to understand the flow
3. **Try SimpleRAG** on a document-heavy question
4. **Ingest more tables** as needed for your questions

### Processing Questions
1. **Start with manual mode** to understand answer schemas
2. **Use SimpleRAG** for document-retrieval questions
3. **Use hybrid mode** for quantitative questions requiring structured data
4. **Always manually verify** LLM outputs before entering values
5. **Save frequently** (auto-saves after each question)

### Best Practices
- Process questions in small batches (5-10 at a time)
- Use `--start` and `--end` to resume from where you left off
- Keep existing `answers.csv` as backup before re-running
- Verify CSV format matches requirements exactly
- Test retrieval quality before full automation

## 🎓 Key Design Decisions

1. **Hybrid Architecture**: Combines documents (PDFs) with structured data (parquet) because questions span both
2. **Flexible Retrieval**: Multiple search strategies (semantic, hybrid, multi-table) for experimentation
3. **Manual Extraction**: LLM generates answers but user extracts structured values to ensure accuracy
4. **Resumable**: Auto-save + load existing answers allows stopping/starting anytime
5. **Modular Design**: Can use retrieval utils independently of RAG, or RAG independently of main.py

## 🚦 Current Status

✅ **Completed:**
- Document ingestion pipeline
- Retrieval utilities with all features
- DSPy RAG modules (Simple + Hybrid)
- Question answering interface
- CSV submission generation
- Comprehensive documentation

⚠️ **Needs Configuration:**
- LLM API keys in `.env`
- Model selection in `retrieve/modules.py`
- Document ingestion (only annual_reports ingested as test)

💡 **Optional Enhancements:**
- Auto-parse LLM answers to structured values (currently manual)
- Add re-ranking for better retrieval
- Fine-tune embeddings for retail domain
- Add evaluation metrics
- Batch processing for all questions

## 🎯 Next Steps

1. **Set up environment** (`.env` with API keys)
2. **Ingest documents** you need: `uv run python -m embed.ingest_data --table <name>`
3. **Test retrieval**: Verify documents are retrievable
4. **Process questions**: `uv run python main.py --round training-questions --rag-type simple`
5. **Verify CSV**: Check `questions/answers.csv` format
6. **Submit**: Upload to leaderboard!

---

**Built with:** DSPy, LanceDB, OpenAI Embeddings, MarkItDown, Pandas
**Total LOC:** ~1,500 lines across 5 core modules
**Time to build:** Optimized for hackathon speed 🚀
