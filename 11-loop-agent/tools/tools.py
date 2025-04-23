"""
Tools for Human-in-the-Loop LinkedIn Post Generator

This module provides tools for human feedback in the post generation loop.
"""

from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def count_characters(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to count characters in the current post and provide length-based feedback.
    Updates review_status and review_feedback in the state based on length requirements.

    Args:
        tool_context: Context for accessing and updating session state

    Returns:
        Dict[str, Any]: Dictionary containing character count and status information
    """
    current_post = tool_context.state.get("current_post", "")
    char_count = len(current_post)
    MIN_LENGTH = 1000
    MAX_LENGTH = 1500

    print("\n----------- TOOL DEBUG -----------")
    print(f"Checking post length: {char_count} characters")
    print("----------------------------------\n")

    if char_count < MIN_LENGTH:
        chars_needed = MIN_LENGTH - char_count
        tool_context.state["review_status"] = "fail"
        tool_context.state["review_feedback"] = (
            f"Post is too short. Add {chars_needed} more characters to reach minimum length of {MIN_LENGTH}."
        )
        return {
            "result": "too_short",
            "char_count": char_count,
            "chars_needed": chars_needed,
        }
    elif char_count > MAX_LENGTH:
        chars_to_remove = char_count - MAX_LENGTH
        tool_context.state["review_status"] = "fail"
        tool_context.state["review_feedback"] = (
            f"Post is too long. Remove {chars_to_remove} characters to meet maximum length of {MAX_LENGTH}."
        )
        return {
            "result": "too_long",
            "char_count": char_count,
            "chars_to_remove": chars_to_remove,
        }
    else:
        tool_context.state["review_status"] = "pass"
        tool_context.state["review_feedback"] = (
            f"Post length is good ({char_count} characters)."
        )
        return {"result": "good", "char_count": char_count}
