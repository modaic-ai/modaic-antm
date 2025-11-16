import sys
from pathlib import Path
from typing import List, Dict, Optional, Union, Literal
import warnings

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from db.lancedb import db
from embed.utils import create_embeddings


def list_tables() -> List[str]:
    """
    List all available tables in LanceDB.

    Returns:
        List of table names
    """
    return db.table_names()


def get_table_info(table_name: str) -> Dict:
    """
    Get information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Dictionary with table metadata (name, row count, etc.)
    """
    if table_name not in list_tables():
        raise ValueError(
            f"Table '{table_name}' not found. Available tables: {list_tables()}"
        )

    table = db.open_table(table_name)
    return {
        "name": table_name,
        "row_count": table.count_rows(),
        "schema": table.schema,
    }


def search_table(
    table_name: str,
    query: str,
    k: int = 5,
    return_type: Literal["content", "dict", "list"] = "content",
    include_distance: bool = False,
    distance_threshold: Optional[float] = None,
    prefilter: Optional[str] = None,
) -> Union[str, List[Dict], List[str]]:
    """
    Search a single table with a text query using vector similarity.

    Args:
        table_name: Name of the table to search
        query: Search query text
        k: Number of results to return (default: 5)
        return_type: Format of results:
            - "content": Concatenated text content (good for LLM context)
            - "dict": List of full dictionaries with all fields
            - "list": List of content strings only
        include_distance: Whether to include distance scores (only for dict return_type)
        distance_threshold: Maximum distance threshold (filter out results above this)
        prefilter: SQL-like filter to apply before search (e.g., "filename LIKE '%2022%'")

    Returns:
        Search results in specified format
    """
    if table_name not in list_tables():
        raise ValueError(
            f"Table '{table_name}' not found. Available tables: {list_tables()}"
        )

    # Get the table
    table = db.open_table(table_name)

    # Create query embedding
    query_embedding = create_embeddings([query])[0]

    # Build search query
    search_query = table.search(query_embedding).limit(k)

    # Apply prefilter if provided
    if prefilter:
        search_query = search_query.where(prefilter)

    # Execute search
    results = search_query.to_list()

    # Apply distance threshold if provided
    if distance_threshold is not None:
        results = [
            r for r in results if r.get("_distance", float("inf")) <= distance_threshold
        ]

    # Format results based on return_type
    if return_type == "content":
        # Concatenate all content with separators
        content_parts = []
        for i, result in enumerate(results):
            header = f"--- Document {i + 1}: {result['filename']} ---"
            if include_distance:
                header += f" (distance: {result.get('_distance', 'N/A'):.4f})"
            content_parts.append(f"{header}\n{result['content']}")
        return "\n\n".join(content_parts)

    elif return_type == "list":
        # Return list of content strings
        return [result["content"] for result in results]

    elif return_type == "dict":
        # Return full dictionaries
        if not include_distance:
            # Remove distance field
            for result in results:
                result.pop("_distance", None)
        return results

    else:
        raise ValueError(
            f"Invalid return_type: {return_type}. Must be 'content', 'dict', or 'list'"
        )


def search_multiple_tables(
    table_names: List[str],
    query: str,
    k_per_table: int = 5,
    total_k: Optional[int] = None,
    return_type: Literal["content", "dict", "list"] = "content",
    merge_strategy: Literal["concatenate", "interleave", "best"] = "concatenate",
    include_distance: bool = False,
    distance_threshold: Optional[float] = None,
) -> Union[str, List[Dict], List[str]]:
    """
    Search multiple tables and combine results.

    Args:
        table_names: List of table names to search
        query: Search query text
        k_per_table: Number of results to retrieve from each table
        total_k: Total number of results to return after merging (None for all)
        return_type: Format of results (same as search_table)
        merge_strategy: How to merge results:
            - "concatenate": Append results from each table sequentially
            - "interleave": Alternate between tables
            - "best": Take top-k by distance across all tables
        include_distance: Whether to include distance scores
        distance_threshold: Maximum distance threshold

    Returns:
        Combined search results in specified format
    """
    all_results = []

    # Search each table
    for table_name in table_names:
        if table_name not in list_tables():
            warnings.warn(f"Table '{table_name}' not found, skipping")
            continue

        results = search_table(
            table_name=table_name,
            query=query,
            k=k_per_table,
            return_type="dict",
            include_distance=True,
            distance_threshold=distance_threshold,
        )

        # Add table name to each result
        for result in results:
            result["_table"] = table_name

        all_results.extend(results)

    # Merge results based on strategy
    if merge_strategy == "concatenate":
        merged = all_results

    elif merge_strategy == "interleave":
        # Interleave results from different tables
        merged = []
        max_len = max(k_per_table, len(all_results) // len(table_names))
        for i in range(max_len):
            for table_name in table_names:
                table_results = [
                    r for r in all_results if r.get("_table") == table_name
                ]
                if i < len(table_results):
                    merged.append(table_results[i])

    elif merge_strategy == "best":
        # Sort by distance and take top results
        merged = sorted(all_results, key=lambda x: x.get("_distance", float("inf")))

    else:
        raise ValueError(f"Invalid merge_strategy: {merge_strategy}")

    # Limit total results if specified
    if total_k is not None:
        merged = merged[:total_k]

    # Format results
    if return_type == "content":
        content_parts = []
        for i, result in enumerate(merged):
            header = (
                f"--- Document {i + 1} [{result['_table']}]: {result['filename']} ---"
            )
            if include_distance:
                header += f" (distance: {result.get('_distance', 'N/A'):.4f})"
            content_parts.append(f"{header}\n{result['content']}")
        return "\n\n".join(content_parts)

    elif return_type == "list":
        return [result["content"] for result in merged]

    elif return_type == "dict":
        if not include_distance:
            for result in merged:
                result.pop("_distance", None)
        return merged

    else:
        raise ValueError(f"Invalid return_type: {return_type}")


def hybrid_search(
    table_names: Union[str, List[str]],
    query: str,
    k: int = 5,
    semantic_weight: float = 0.7,
    keyword_boost_terms: Optional[List[str]] = None,
    return_type: Literal["content", "dict", "list"] = "content",
    include_distance: bool = False,
) -> Union[str, List[Dict], List[str]]:
    """
    Perform hybrid search combining semantic and keyword-based filtering.

    Args:
        table_names: Single table name or list of table names
        query: Search query text
        k: Number of results to return
        semantic_weight: Weight for semantic search (0-1, where 1 is pure semantic)
        keyword_boost_terms: Optional list of keywords to boost in results
        return_type: Format of results
        include_distance: Whether to include distance scores

    Returns:
        Search results with hybrid ranking
    """
    # Convert single table to list
    if isinstance(table_names, str):
        table_names = [table_names]

    # Perform semantic search
    if len(table_names) == 1:
        results = search_table(
            table_name=table_names[0],
            query=query,
            k=k * 2,  # Get more results for re-ranking
            return_type="dict",
            include_distance=True,
        )
    else:
        results = search_multiple_tables(
            table_names=table_names,
            query=query,
            k_per_table=k,
            return_type="dict",
            include_distance=True,
        )

    # Apply keyword boosting if specified
    if keyword_boost_terms:
        for result in results:
            # Count keyword matches
            content_lower = result["content"].lower()
            keyword_matches = sum(
                1 for term in keyword_boost_terms if term.lower() in content_lower
            )

            # Adjust score (lower distance is better, so subtract boost)
            keyword_boost = keyword_matches * (1 - semantic_weight) * 0.1
            result["_distance"] = result.get("_distance", 1.0) - keyword_boost

    # Re-rank by adjusted distance
    results = sorted(results, key=lambda x: x.get("_distance", float("inf")))[:k]

    # Format results
    if return_type == "content":
        content_parts = []
        for i, result in enumerate(results):
            table_info = f" [{result['_table']}]" if "_table" in result else ""
            header = f"--- Document {i + 1}{table_info}: {result['filename']} ---"
            if include_distance:
                header += f" (score: {result.get('_distance', 'N/A'):.4f})"
            content_parts.append(f"{header}\n{result['content']}")
        return "\n\n".join(content_parts)

    elif return_type == "list":
        return [result["content"] for result in results]

    elif return_type == "dict":
        if not include_distance:
            for result in results:
                result.pop("_distance", None)
        return results

    else:
        raise ValueError(f"Invalid return_type: {return_type}")


def get_documents_by_filename(
    table_name: str,
    filename_pattern: str,
    return_type: Literal["content", "dict", "list"] = "content",
) -> Union[str, List[Dict], List[str]]:
    """
    Retrieve documents by filename pattern.

    Args:
        table_name: Name of the table
        filename_pattern: SQL LIKE pattern (e.g., '%2022%', 'AnnualReport%')
        return_type: Format of results

    Returns:
        Matching documents
    """
    if table_name not in list_tables():
        raise ValueError(
            f"Table '{table_name}' not found. Available tables: {list_tables()}"
        )

    table = db.open_table(table_name)

    # Use LanceDB filtering
    # Note: For remote tables, we need to search with a dummy query and filter
    # Create a neutral embedding
    neutral_query = "document"
    query_embedding = create_embeddings([neutral_query])[0]

    # Search with large limit and filename filter
    results = (
        table.search(query_embedding)
        .where(f"filename LIKE '{filename_pattern}'")
        .limit(1000)
        .to_list()
    )

    # Format results
    if return_type == "content":
        content_parts = []
        for i, result in enumerate(results):
            header = f"--- Document {i + 1}: {result['filename']} ---"
            content_parts.append(f"{header}\n{result['content']}")
        return "\n\n".join(content_parts)

    elif return_type == "list":
        return [result["content"] for result in results]

    elif return_type == "dict":
        # Remove vector and distance fields for cleaner output
        for result in results:
            result.pop("vector", None)
            result.pop("_distance", None)
        return results

    else:
        raise ValueError(f"Invalid return_type: {return_type}")
