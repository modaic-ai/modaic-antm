# Quick Start Guide

## 1. Setup Environment

```bash
# Already done:
uv sync
```

## 2. Test the System

```bash
# Test question parsing (no API calls needed)
uv run python -c "
from main import QuestionRound
from pathlib import Path

round_obj = QuestionRound(Path('questions/training-questions.md'))
print(f'✓ Loaded {len(round_obj.questions)} questions')
print(f'First question schema: {round_obj.get_answer_schema(0)}')
"
```

## 3. Answer Questions (Manual Mode)

```bash
# Process first 3 questions manually (no RAG, no API calls)
uv run python main.py --round training-questions --rag-type none --start 0 --end 3
```

## 4. Answer Questions (With RAG)

```bash
# Make sure you have API keys in .env first!
uv run python main.py --round training-questions --rag-type simple --start 0 --end 3
```

## 5. Check Output

```bash
cat questions/answers.csv
```

## Common Commands

```bash
# Process all training questions
uv run python main.py --round training-questions --rag-type simple

# Process round-1 questions  
uv run python main.py --round round-1-questions --rag-type simple

# Resume from question 5
uv run python main.py --round training-questions --rag-type simple --start 5

# Custom output file
uv run python main.py --round training-questions --output my_answers.csv
```

See `README_USAGE.md` for complete documentation!
