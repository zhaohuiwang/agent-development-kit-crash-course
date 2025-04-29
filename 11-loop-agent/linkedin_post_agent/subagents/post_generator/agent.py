"""
LinkedIn Post Generator Agent

This agent generates or refines LinkedIn posts based on feedback.
"""

from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types

# Constants
GEMINI_MODEL = "gemini-2.0-flash"


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Initialize state variables if they don't exist."""
    state = callback_context.state

    if "current_post" not in state:
        state["current_post"] = ""
    if "review_feedback" not in state:
        state["review_feedback"] = ""
    if "review_status" not in state:
        state["review_status"] = ""

    print("\n----------- POST GENERATOR INITIALIZATION -----------")
    print(f"Current post exists: {'Yes' if state['current_post'] else 'No'}")
    print(f"Review status: {state['review_status']}")
    print(f"Has feedback: {'Yes' if state['review_feedback'] else 'No'}")
    print("---------------------------------------------------\n")

    return None


# Define the Post Generator Agent
post_generator = LlmAgent(
    name="LinkedInPostGenerator",
    model=GEMINI_MODEL,
    instruction="""You are a LinkedIn Post Generator.

    Your task is to create or refine a LinkedIn post about an Agent Development Kit (ADK) tutorial by @aiwithbrandon.
    
    ## STEP 1: DETERMINE ACTION
    - If the current post is empty, this is the initial generation and you need to create a new post.
    - If the review_status is "pass", no changes are needed and you can return the current post.
    - Otherwise, refine the post based on the review feedback.
    
    ## STEP 2: CONTENT REQUIREMENTS
    When creating or refining, ensure the post includes:
    1. Excitement about learning from the tutorial
    2. Specific aspects of ADK learned:
       - Basic agent implementation (basic-agent)
       - Tool integration (tool-agent)
       - Using LiteLLM (litellm-agent)
       - Managing sessions and memory
       - Persistent storage capabilities
       - Multi-agent orchestration
       - Stateful multi-agent systems
       - Callback systems
       - Sequential agents for pipeline workflows
       - Parallel agents for concurrent operations
       - Loop agents for iterative refinement
    3. Brief statement about improving AI applications
    4. Mention/tag of @aiwithbrandon
    5. Clear call-to-action for connections
    
    ## STEP 3: STYLE REQUIREMENTS
    - Professional and conversational tone
    - Between 1000-1500 characters
    - NO emojis
    - NO hashtags
    - Show genuine enthusiasm
    - Highlight practical applications
    
    ## OUTPUT INSTRUCTIONS
    - Return ONLY the post content
    - Do not add formatting markers or explanations

    Here is the current post:
    {current_post}

    Here is the review feedback:
    {review_feedback}

    Here is the review status:
    {review_status}
    """,
    description="Generates or refines LinkedIn posts based on automated review feedback",
    output_key="current_post",
    before_agent_callback=before_agent_callback,
)
