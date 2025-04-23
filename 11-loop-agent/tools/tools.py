"""
Tools for Human-in-the-Loop LinkedIn Post Generator

This module provides tools for human feedback in the post generation loop.
"""

import time
from typing import Any, Dict

from google.adk.tools.tool_context import ToolContext


def get_human_feedback(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Console-based tool to get human feedback on the generated LinkedIn post.
    Sets feedback_status and feedback_content in the state.

    Args:
        tool_context: Context for accessing and updating session state

    Returns:
        Dict[str, Any]: Dictionary indicating processing status.
    """
    # Get the current post from state to display it
    current_post = tool_context.state.get("current_post", "")

    print("\n----------- TOOL DEBUG -----------")
    print(f"Current post in state: {len(current_post)} chars")
    print("----------------------------------\n")

    print("\n========== HUMAN FEEDBACK REQUESTED ==========")
    print("Please review the LinkedIn post:")
    print("\n" + current_post + "\n")
    print("Options:")
    print("1. Approve post (type 'approve' or 'a')")
    print("2. Revise post (provide specific feedback)")
    print("==============================================")

    try:
        # Get user input with a prompt
        user_feedback = input("Your feedback: ").strip()

        print("\n----------- TOOL DEBUG -----------")
        print(f"User feedback: '{user_feedback}'")
        print("----------------------------------\n")

        # Process the feedback
        if user_feedback.lower() in ["approve", "a"]:
            tool_context.state["feedback_status"] = "approved"
            tool_context.state["feedback_content"] = "Post approved by user."

            # IMPORTANT: Don't modify the current_post
            print("\n----------- TOOL DEBUG -----------")
            print("Status: approved")
            print("----------------------------------\n")

            # Return a simple confirmation - THIS TEXT WILL NOT BE USED AS A POST
            return {"result": "Feedback: approved"}
        else:
            # Store revision feedback in state
            tool_context.state["feedback_status"] = "revise"
            tool_context.state["feedback_content"] = user_feedback

            # IMPORTANT: Don't modify the current_post
            print("\n----------- TOOL DEBUG -----------")
            print(f"Status: revise, Content: '{user_feedback}'")
            print("----------------------------------\n")

            # Return a simple confirmation - THIS TEXT WILL NOT BE USED AS A POST
            return {"result": "Feedback received for revision"}

    except Exception as e:
        tool_context.state["feedback_status"] = "error"
        tool_context.state["feedback_content"] = f"Error getting feedback: {str(e)}"

        # Return error info
        return {"result": f"Error occurred: {str(e)}"}
