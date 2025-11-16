import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd
from tqdm import tqdm

# Add parent directory to path to import local modules
sys.path.append(str(Path(__file__).parent.parent))

from embed.utils import convert_pdf_to_markdown, create_embeddings
from db.lancedb import db, table_names


def get_pdf_files(table_name: str, dataset_path: str = "dataset") -> List[Path]:
    """
    Get all PDF files for a given table name.

    Args:
        table_name: Name of the table/directory (e.g., 'annual_reports')
        dataset_path: Base path to the dataset directory

    Returns:
        List of Path objects pointing to PDF files
    """
    pdf_dir = Path(dataset_path) / table_name / "pdf"

    if not pdf_dir.exists():
        print(f"Warning: Directory {pdf_dir} does not exist")
        return []

    pdf_files = list(pdf_dir.glob("*.pdf"))
    return pdf_files


def process_pdf_batch(pdf_files: List[Path], batch_size: int = 10) -> List[Dict]:
    """
    Process a batch of PDF files into documents with embeddings.

    Args:
        pdf_files: List of PDF file paths
        batch_size: Number of documents to embed at once

    Returns:
        List of dictionaries containing document data
    """
    documents = []

    print(f"Converting {len(pdf_files)} PDFs to markdown...")
    for pdf_path in tqdm(pdf_files, desc="Converting PDFs"):
        try:
            # Convert PDF to markdown
            markdown_content = convert_pdf_to_markdown(str(pdf_path))

            documents.append(
                {
                    "filename": pdf_path.name,
                    "filepath": str(pdf_path),
                    "content": markdown_content,
                }
            )
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            continue

    if not documents:
        return []

    # Extract content for embedding
    contents = [doc["content"] for doc in documents]

    print(f"Creating embeddings for {len(contents)} documents...")
    # Create embeddings in batches
    all_embeddings = []
    for i in tqdm(range(0, len(contents), batch_size), desc="Creating embeddings"):
        batch = contents[i : i + batch_size]
        embeddings = create_embeddings(batch, batch_size=len(batch))
        all_embeddings.extend(embeddings)

    # Add embeddings to documents
    for doc, embedding in zip(documents, all_embeddings):
        doc["vector"] = embedding

    return documents


def ingest_table(
    table_name: str,
    dataset_path: str = "dataset",
    batch_size: int = 10,
    max_files: int = None,
):
    """
    Ingest all PDFs from a table directory into LanceDB.

    Args:
        table_name: Name of the table/directory
        dataset_path: Base path to the dataset directory
        batch_size: Number of documents to embed at once
        max_files: Maximum number of files to process (None for all)
    """
    print(f"\n{'=' * 60}")
    print(f"Processing table: {table_name}")
    print(f"{'=' * 60}")

    # Get all PDF files
    pdf_files = get_pdf_files(table_name, dataset_path)

    if not pdf_files:
        print(f"No PDF files found for {table_name}")
        return

    print(f"Found {len(pdf_files)} PDF files")

    # Limit files if specified
    if max_files is not None:
        pdf_files = pdf_files[:max_files]
        print(f"Processing first {len(pdf_files)} files")

    # Process PDFs
    documents = process_pdf_batch(pdf_files, batch_size)

    if not documents:
        print(f"No documents processed for {table_name}")
        return

    # Convert to DataFrame for LanceDB
    df = pd.DataFrame(documents)

    # Create or overwrite table in LanceDB
    print(f"Storing {len(documents)} documents in LanceDB table '{table_name}'...")
    try:
        # Check if table exists
        existing_tables = db.table_names()
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists. Dropping and recreating...")
            db.drop_table(table_name)

        # Create new table
        table = db.create_table(table_name, data=df)
        print(
            f"Successfully created table '{table_name}' with {len(documents)} documents"
        )

    except Exception as e:
        print(f"Error storing data in LanceDB: {e}")
        raise


def ingest_all_tables(
    dataset_path: str = "dataset", batch_size: int = 10, max_files_per_table: int = None
):
    """
    Ingest all tables defined in table_names.

    Args:
        dataset_path: Base path to the dataset directory
        batch_size: Number of documents to embed at once
        max_files_per_table: Maximum number of files to process per table (None for all)
    """
    print(f"\nStarting ingestion for {len(table_names)} tables...")
    print(f"Tables to process: {', '.join(table_names)}\n")

    for table_name in table_names:
        try:
            ingest_table(table_name, dataset_path, batch_size, max_files_per_table)
        except Exception as e:
            print(f"Failed to ingest table '{table_name}': {e}")
            continue

    print(f"\n{'=' * 60}")
    print("Ingestion complete!")
    print(f"{'=' * 60}")

    # Show final table statistics
    print("\nFinal table statistics:")
    for table_name in db.table_names():
        try:
            table = db.open_table(table_name)
            count = table.count_rows()
            print(f"  {table_name}: {count} documents")
        except Exception as e:
            print(f"  {table_name}: Error - {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest PDF documents into LanceDB")
    parser.add_argument(
        "--table",
        type=str,
        help="Specific table to ingest (if not specified, ingests all tables)",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="dataset",
        help="Path to dataset directory (default: dataset)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for embedding creation (default: 10)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of files to process per table (default: all files)",
    )

    args = parser.parse_args()

    if args.table:
        # Ingest specific table
        if args.table not in table_names:
            print(f"Error: '{args.table}' is not a valid table name")
            print(f"Valid tables: {', '.join(table_names)}")
            sys.exit(1)

        ingest_table(args.table, args.dataset_path, args.batch_size, args.max_files)
    else:
        # Ingest all tables
        ingest_all_tables(args.dataset_path, args.batch_size, args.max_files)
