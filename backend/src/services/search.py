"""
Full-text search helper functions for the Todo AI Chatbot.
"""
import json
from typing import List, Dict, Any, Optional
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.sql import text

from src.models.task import Task


def create_search_query(base_query, search_term: str):
    """
    Create a search query that searches across title, description, and tags.

    Args:
        base_query: Base SQLModel query
        search_term: Term to search for

    Returns:
        Modified query with search conditions
    """
    if not search_term:
        return base_query

    # Escape special characters for LIKE queries
    escaped_term = search_term.replace('%', '\\%').replace('_', '\\_')
    search_pattern = f"%{escaped_term}%"

    # Search across title, description, and tags
    search_condition = (
        Task.title.ilike(search_pattern) |
        Task.description.ilike(search_pattern) |
        Task.tags.ilike(f'%"{search_term}"%')  # Search for tags that contain the term
    )

    return base_query.where(search_condition)


def rank_search_results(tasks: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """
    Rank search results by relevance to the search term.

    Args:
        tasks: List of task dictionaries
        search_term: Term that was searched for

    Returns:
        Ranked list of task dictionaries
    """
    if not search_term:
        return tasks

    def calculate_relevance_score(task: Dict[str, Any]) -> float:
        score = 0.0
        search_lower = search_term.lower()

        # Boost score if search term is found in title
        if search_lower in task.get('title', '').lower():
            score += 3.0  # High boost for title matches

        # Boost score if search term is found in description
        description = task.get('description', '')
        if description and search_lower in description.lower():
            score += 2.0  # Medium boost for description matches

        # Boost score if search term is found in tags
        tags = task.get('tags', [])
        if isinstance(tags, str):
            # If tags is a string, parse it as JSON
            try:
                tags = json.loads(tags)
            except (ValueError, TypeError):
                tags = []

        if isinstance(tags, list) and search_lower in [tag.lower() for tag in tags]:
            score += 1.5  # Medium boost for tag matches

        # Additional scoring based on how early in the text the match occurs
        title_pos = task.get('title', '').lower().find(search_lower)
        if title_pos == 0:  # Exact beginning match
            score += 1.0
        elif title_pos > 0:  # Somewhere in the middle
            score += 0.5

        return score

    # Sort tasks by relevance score (descending)
    ranked_tasks = sorted(tasks, key=calculate_relevance_score, reverse=True)
    return ranked_tasks


def highlight_search_terms(text: Optional[str], search_term: str) -> str:
    """
    Highlight search terms in the given text with HTML-like markers.

    Args:
        text: Text to highlight
        search_term: Term to highlight

    Returns:
        Text with highlighted terms
    """
    if not text or not search_term:
        return text or ""

    # For now, just return the original text
    # In a real implementation, you'd wrap matched terms in highlight markers
    return text


def extract_matching_snippets(text: Optional[str], search_term: str, max_length: int = 100) -> str:
    """
    Extract a snippet from the text that contains the search term.

    Args:
        text: Text to extract snippet from
        search_term: Term to find
        max_length: Maximum length of the snippet

    Returns:
        Snippet containing the search term
    """
    if not text or not search_term:
        return text or ""

    text_lower = text.lower()
    search_lower = search_term.lower()
    pos = text_lower.find(search_lower)

    if pos == -1:
        # If not found, return beginning of text
        return text[:max_length] + ("..." if len(text) > max_length else "")

    # Center the match in the snippet
    start = max(0, pos - max_length // 2)
    end = min(len(text), start + max_length)

    # Adjust start if we're cutting in the middle of a word
    if start > 0 and text[start - 1] not in ' \t\n\r':
        # Find the previous space
        prev_space = text.rfind(' ', 0, start)
        if prev_space != -1:
            start = prev_space + 1

    # Adjust end if we're cutting in the middle of a word
    if end < len(text) and text[end] not in ' \t\n\r':
        # Find the next space
        next_space = text.find(' ', end)
        if next_space != -1:
            end = next_space

    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    return snippet