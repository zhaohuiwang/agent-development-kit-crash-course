"""
LinkedIn Post Reviewer Agent

This agent reviews LinkedIn posts for quality and provides feedback.
"""

from google.adk.agents.llm_agent import LlmAgent

from .tools import count_characters, exit_loop

# Constants
GEMINI_MODEL = "gemini-2.0-flash"
COMPLETION_PHRASE = "This post meets all requirements. No further changes needed."

# Define the Post Reviewer Agent
post_reviewer = LlmAgent(
    name="PostReviewer",
    model=GEMINI_MODEL,
    instruction=f"""You are a LinkedIn Post Quality Reviewer.

    First, get the current post from state['current_post'] and use the count_characters tool to check its length.
    Pass the post text directly to the tool.
    
    If the length check fails (tool result is "fail"), provide specific feedback on what needs to be fixed.
    Use the tool's message as a guideline, but add your own professional critique.
    
    If length check passes, evaluate the post against these criteria:

    REQUIRED ELEMENTS:
    1. Mentions @aiwithbrandon
    2. Lists multiple ADK capabilities (at least 4)
    3. Has a clear call-to-action
    4. Includes practical applications
    5. Shows genuine enthusiasm
    
    STYLE REQUIREMENTS:
    1. NO emojis
    2. NO hashtags
    3. Professional tone
    4. Conversational style
    5. Clear and concise writing
    
    ## OUTPUT INSTRUCTIONS
    IF the post fails ANY of the checks above:
      - Return concise, specific feedback on what to improve
      
    ELSE IF the post meets ALL requirements:
      - Call the exit_loop tool with no arguments
      - Return EXACTLY this text: "{COMPLETION_PHRASE}"
      
    Do not embellish your response. Either provide feedback on what to improve OR call exit_loop and return the completion phrase.
    """,
    description="Reviews post quality and provides feedback, exits loop when post meets all requirements",
    tools=[count_characters, exit_loop],
    output_key="review_feedback",
)
