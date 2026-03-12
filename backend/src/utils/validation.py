"""
Utility functions for validating priority and tags in the Todo AI Chatbot.
"""

import re
from typing import List, Optional


def validate_priority(priority: Optional[str]) -> bool:
    """
    Validate that the priority is one of the allowed values: 'high', 'medium', 'low'.

    Args:
        priority: The priority level to validate

    Returns:
        True if valid, False otherwise
    """
    if priority is None:
        return True  # Allow None for optional priority

    allowed_priorities = {"high", "medium", "low"}
    return priority.lower() in allowed_priorities


def sanitize_priority(priority: Optional[str]) -> str:
    """
    Sanitize and normalize the priority value.

    Args:
        priority: The priority level to sanitize

    Returns:
        The sanitized priority value, defaults to 'medium' if invalid or None
    """
    if priority is None:
        return "medium"

    priority_lower = priority.lower().strip()
    allowed_priorities = {"high", "medium", "low"}

    if priority_lower in allowed_priorities:
        return priority_lower
    else:
        return "medium"  # Default to medium if invalid


def validate_tags(tags: Optional[List[str]]) -> tuple[bool, Optional[str]]:
    """
    Validate the tags list according to the specification.

    Args:
        tags: List of tags to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if tags is None:
        return True, None

    if not isinstance(tags, list):
        return False, "Tags must be a list of strings"

    if len(tags) > 10:
        return False, "Maximum of 10 tags per task allowed"

    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            return False, f"Tag at index {i} must be a string"

        if len(tag) < 1 or len(tag) > 50:
            return False, f"Tag '{tag}' length must be between 1 and 50 characters"

        # Check if tag matches allowed pattern: alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
            return False, f"Tag '{tag}' contains invalid characters. Only alphanumeric, hyphens, and underscores are allowed"

    # Check for duplicates
    if len(tags) != len(set(tags)):
        return False, "Duplicate tags are not allowed"

    return True, None


def sanitize_tags(tags: Optional[List[str]]) -> List[str]:
    """
    Sanitize the tags list according to the specification.

    Args:
        tags: List of tags to sanitize

    Returns:
        Sanitized list of tags
    """
    if tags is None:
        return []

    if not isinstance(tags, list):
        return []

    # Trim and clean each tag
    sanitized_tags = []
    seen_tags = set()

    for tag in tags:
        if isinstance(tag, str):
            # Trim whitespace and convert to lowercase
            clean_tag = tag.strip().lower()

            # Skip empty tags or tags that don't match the pattern
            if clean_tag and re.match(r'^[a-zA-Z0-9_-]+$', clean_tag):
                # Avoid duplicates while preserving order
                if clean_tag not in seen_tags:
                    sanitized_tags.append(clean_tag)
                    seen_tags.add(clean_tag)

                    # Limit to 10 tags
                    if len(sanitized_tags) >= 10:
                        break

    return sanitized_tags


def validate_and_sanitize_priority(priority: Optional[str]) -> tuple[bool, str, Optional[str]]:
    """
    Validate and sanitize a priority value.

    Args:
        priority: The priority to validate and sanitize

    Returns:
        Tuple of (is_valid, sanitized_value, error_message)
    """
    if priority is None:
        return True, "medium", None

    sanitized = sanitize_priority(priority)
    is_valid = validate_priority(sanitized)

    if is_valid:
        return True, sanitized, None
    else:
        return False, "medium", f"Invalid priority value: {priority}. Must be one of: high, medium, low"


def validate_and_sanitize_tags(tags: Optional[List[str]]) -> tuple[bool, List[str], Optional[str]]:
    """
    Validate and sanitize a tags list.

    Args:
        tags: The tags list to validate and sanitize

    Returns:
        Tuple of (is_valid, sanitized_list, error_message)
    """
    is_valid, error_msg = validate_tags(tags)

    if is_valid:
        sanitized = sanitize_tags(tags)
        return True, sanitized, None
    else:
        return False, [], error_msg