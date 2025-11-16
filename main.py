"""
Retail Analytics Question Answering System

This script provides an interface for answering retail analytics questions
and generating submission CSV files in the required format.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from retrieve.modules import RetailAnalyticsRAG, SimpleRAG


class QuestionRound:
    """Represents a round of questions with their schema."""

    def __init__(self, round_file: Path):
        self.round_file = round_file
        self.round_name = round_file.stem
        self.questions = self._parse_questions()

    def _parse_questions(self) -> List[Dict[str, Any]]:
        """Parse questions from markdown file."""
        questions = []
        current_question = None

        with open(self.round_file, 'r') as f:
            lines = f.readlines()

        in_json_block = False
        json_buffer = []

        for line in lines:
            # Start of JSON block
            if line.strip().startswith('```json'):
                in_json_block = True
                json_buffer = []
                continue

            # End of JSON block
            if line.strip() == '```' and in_json_block:
                in_json_block = False
                try:
                    question_data = json.loads(''.join(json_buffer))
                    if 'question' in question_data:
                        questions.append(question_data)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse JSON block: {e}")
                continue

            # Collect JSON content
            if in_json_block:
                json_buffer.append(line)

        return questions

    def get_answer_schema(self, question_idx: int) -> List[str]:
        """Get the answer fields for a specific question (excluding 'question' and 'difficulty')."""
        if question_idx >= len(self.questions):
            return []

        question_data = self.questions[question_idx]
        # Filter out metadata fields to get only answer fields
        answer_fields = [
            key for key in question_data.keys()
            if key not in ['question', 'difficulty']
        ]
        return answer_fields


class SubmissionBuilder:
    """Builds submission CSV in the required format."""

    def __init__(self, output_file: str = "questions/answers.csv"):
        self.output_file = Path(output_file)
        self.answers = []

    def add_answer(self, row_index: int, answer_values: List[Any]):
        """
        Add an answer row.

        Args:
            row_index: 0-based index
            answer_values: List of up to 5 answer values (in order)
        """
        # Ensure we have exactly 5 columns (pad with empty strings)
        padded_values = answer_values + [''] * (5 - len(answer_values))
        padded_values = padded_values[:5]  # Truncate if too many

        self.answers.append({
            'row_index': row_index,
            'col_1': padded_values[0],
            'col_2': padded_values[1],
            'col_3': padded_values[2],
            'col_4': padded_values[3],
            'col_5': padded_values[4],
        })

    def save(self):
        """Save answers to CSV file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['row_index', 'col_1', 'col_2', 'col_3', 'col_4', 'col_5']
            )
            writer.writeheader()
            writer.writerows(self.answers)

        print(f"\n✓ Saved {len(self.answers)} answers to {self.output_file}")

    def load_existing(self):
        """Load existing answers from CSV if it exists."""
        if not self.output_file.exists():
            return

        try:
            df = pd.read_csv(self.output_file)
            self.answers = df.to_dict('records')
            print(f"Loaded {len(self.answers)} existing answers from {self.output_file}")
        except Exception as e:
            print(f"Warning: Could not load existing answers: {e}")


class QuestionAnsweringSystem:
    """Main system for answering questions using RAG."""

    def __init__(
        self,
        rag_type: str = "simple",
        num_docs: int = 5,
        use_structured: bool = True,
        use_documents: bool = True
    ):
        """
        Initialize the QA system.

        Args:
            rag_type: "simple" or "hybrid"
            num_docs: Number of documents to retrieve
            use_structured: Whether to use structured data analysis
            use_documents: Whether to use document retrieval
        """
        self.rag_type = rag_type

        if rag_type == "simple":
            self.rag = SimpleRAG(num_docs=num_docs)
        elif rag_type == "hybrid":
            self.rag = RetailAnalyticsRAG(
                num_docs=num_docs,
                use_structured=use_structured,
                use_documents=use_documents
            )
        else:
            raise ValueError(f"Unknown RAG type: {rag_type}")

    def answer_question(self, question: str) -> str:
        """Answer a single question using the RAG system."""
        print(f"\nQuestion: {question}")
        print("Processing with RAG...")

        try:
            result = self.rag(question=question)

            # Extract answer based on RAG type
            if self.rag_type == "simple":
                answer = result.answer
            elif self.rag_type == "hybrid":
                answer = result.final_answer
            else:
                answer = str(result)

            return answer

        except Exception as e:
            print(f"Error answering question: {e}")
            import traceback
            traceback.print_exc()
            return f"ERROR: {str(e)}"

    def parse_answer_to_values(self, answer: str, schema: List[str]) -> List[Any]:
        """
        Parse LLM answer into structured values matching the schema.

        This is a simple implementation - you may want to enhance this
        with more sophisticated parsing or use a structured output signature.
        """
        # TODO: Implement smart parsing based on schema
        # For now, return the raw answer
        print(f"\nSchema fields: {schema}")
        print(f"Answer: {answer}")
        print("\n⚠ Manual parsing required - please extract values and enter below:")

        values = []
        for field in schema:
            value = input(f"  {field}: ").strip()
            # Try to convert to appropriate type
            if value:
                try:
                    # Try int first
                    if '.' not in value:
                        values.append(int(value))
                    else:
                        values.append(float(value))
                except ValueError:
                    # Keep as string
                    values.append(value)
            else:
                values.append('')

        return values


def process_round(
    round_name: str,
    qa_system: Optional[QuestionAnsweringSystem] = None,
    start_idx: int = 0,
    end_idx: Optional[int] = None,
    interactive: bool = True,
    output_file: str = "questions/answers.csv"
):
    """
    Process a round of questions.

    Args:
        round_name: Name of the round (e.g., "training-questions", "round-1-questions")
        qa_system: QA system to use (if None, manual mode)
        start_idx: Starting question index (0-based)
        end_idx: Ending question index (exclusive, None for all)
        interactive: Whether to allow manual input/correction
        output_file: Path to output CSV file
    """
    # Load questions
    round_file = Path("questions") / f"{round_name}.md"
    if not round_file.exists():
        print(f"Error: Question file not found: {round_file}")
        return

    round_obj = QuestionRound(round_file)
    print(f"\n{'='*80}")
    print(f"Processing: {round_name}")
    print(f"Total questions: {len(round_obj.questions)}")
    print(f"{'='*80}")

    # Load or create submission builder
    submission = SubmissionBuilder(output_file=output_file)
    if interactive:
        submission.load_existing()

    # Determine question range
    questions_to_process = round_obj.questions[start_idx:end_idx]
    if end_idx is None:
        end_idx = len(round_obj.questions)

    # Process each question
    for i, question_data in enumerate(questions_to_process):
        actual_idx = start_idx + i
        question_text = question_data['question']

        print(f"\n{'='*80}")
        print(f"Question {actual_idx + 1}/{len(round_obj.questions)}")
        print(f"{'='*80}")
        print(f"Q: {question_text}")

        # Get answer schema
        schema = round_obj.get_answer_schema(actual_idx)
        print(f"\nExpected answer fields: {schema}")

        # Get answer
        if qa_system:
            # Use RAG system
            answer = qa_system.answer_question(question_text)
            print(f"\nRAG Answer:\n{answer}")

            if interactive:
                # Allow manual parsing/correction
                print("\n--- Manual value extraction ---")
                values = qa_system.parse_answer_to_values(answer, schema)
            else:
                # Auto-parse (you'd need to implement this)
                values = qa_system.parse_answer_to_values(answer, schema)
        else:
            # Manual mode - user enters values
            print("\n--- Manual entry mode ---")
            values = []
            for field in schema:
                value = input(f"  {field}: ").strip()
                if value:
                    try:
                        if '.' not in value:
                            values.append(int(value))
                        else:
                            values.append(float(value))
                    except ValueError:
                        values.append(value)
                else:
                    values.append('')

        # Add to submission
        submission.add_answer(actual_idx, values)
        print(f"\n✓ Added answer: {values}")

        # Save after each question (in case of interruption)
        submission.save()

        # Ask to continue (in interactive mode)
        if interactive and actual_idx < end_idx - 1:
            cont = input("\nContinue to next question? (y/n): ").strip().lower()
            if cont != 'y':
                print("Stopping. Progress saved.")
                break

    print(f"\n{'='*80}")
    print(f"Round complete! Processed {len(questions_to_process)} questions.")
    print(f"{'='*80}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Retail Analytics Question Answering System"
    )

    parser.add_argument(
        "--round",
        type=str,
        default="training-questions",
        help="Round to process (e.g., 'training-questions', 'round-1-questions')"
    )
    parser.add_argument(
        "--rag-type",
        type=str,
        choices=["simple", "hybrid", "none"],
        default="simple",
        help="Type of RAG to use (simple, hybrid, or none for manual)"
    )
    parser.add_argument(
        "--num-docs",
        type=int,
        default=5,
        help="Number of documents to retrieve"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Starting question index (0-based)"
    )
    parser.add_argument(
        "--end",
        type=int,
        help="Ending question index (exclusive)"
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive mode"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="questions/answers.csv",
        help="Output CSV file path"
    )

    args = parser.parse_args()

    # Initialize QA system
    qa_system = None
    if args.rag_type != "none":
        print(f"Initializing {args.rag_type.upper()} RAG system...")
        try:
            qa_system = QuestionAnsweringSystem(
                rag_type=args.rag_type,
                num_docs=args.num_docs,
                use_structured=True,
                use_documents=True
            )
            print("✓ RAG system ready")
        except Exception as e:
            print(f"⚠ Failed to initialize RAG: {e}")
            print("Continuing in manual mode...")

    # Process round
    process_round(
        round_name=args.round,
        qa_system=qa_system,
        start_idx=args.start,
        end_idx=args.end,
        interactive=not args.no_interactive,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
