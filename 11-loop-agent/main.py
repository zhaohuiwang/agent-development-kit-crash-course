from typing import AsyncGenerator

from dotenv import load_dotenv
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from tools.tools import count_characters

load_dotenv()

# Pattern: Iterative Refinement Loop

# --- Constants ---
APP_NAME = "linkedin_post_generator"
USER_ID = "aiwithbrandon"
SESSION_ID = "linkedin_post_session_01"
GEMINI_MODEL = "gemini-2.0-flash"

# --- 1. Define the Post Generator Agent ---
post_generator = LlmAgent(
    name="LinkedInPostGenerator",
    model=GEMINI_MODEL,
    instruction="""You are a LinkedIn Post Generator.

    Your task is to create or refine a LinkedIn post about an Agent Development Kit (ADK) tutorial by @aiwithbrandon.
    
    ## STEP 1: DETERMINE ACTION
    - If this is initial generation (no state['current_post']): Create a new post
    - If state['current_post'] exists and state['review_feedback']: Refine the post based on feedback
    
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
    - Save your post to state['current_post']
    - Return ONLY the post content
    - Do not add formatting markers or explanations
    """,
    description="Generates or refines LinkedIn posts based on automated review feedback",
)

# --- 2. Define the Post Reviewer Agent ---
post_reviewer = LlmAgent(
    name="PostReviewer",
    model=GEMINI_MODEL,
    instruction="""You are a LinkedIn Post Quality Reviewer.

    First, use the count_characters tool to check the post length.
    If the length check fails, return "fail" immediately.
    
    If length is good, evaluate the post in state['current_post'] against these criteria:

    REQUIRED ELEMENTS:
    1. Mentions @aiwithbrandon
    2. Lists multiple ADK capabilities
    3. Has a clear call-to-action
    4. Includes practical applications
    5. Shows enthusiasm
    
    STYLE REQUIREMENTS:
    1. NO emojis
    2. NO hashtags
    3. Professional tone
    4. Conversational style
    5. Clear and concise writing
    
    ## OUTPUT INSTRUCTIONS
    1. Set state['review_status'] to either 'pass' or 'fail'
    2. If 'fail', set state['review_feedback'] to specific improvements needed
    3. Return only 'pass' or 'fail'
    """,
    description="Reviews post quality and provides feedback",
    tools=[count_characters],
)


# --- 3. Define Status Checker Agent ---
class ReviewStatusChecker(BaseAgent):
    """Checks review status and determines if the loop should continue."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        review_status = ctx.session.state.get("review_status", "fail")
        should_stop = review_status == "pass"
        print(f"HERE:Review status: {review_status}")
        print(f"HERE:Should stop: {should_stop}")
        yield Event(
            author=self.name,
            actions=EventActions(escalate=should_stop),
        )


# --- 4. Create the Loop Agent ---
linkedin_post_loop = LoopAgent(
    name="LinkedInPostRefinementLoop",
    max_iterations=10,
    sub_agents=[
        post_generator,
        post_reviewer,
        ReviewStatusChecker(name="ContinuationDecider"),
    ],
)

# --- 5. Setup Session and Runner ---
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=linkedin_post_loop, app_name=APP_NAME, session_service=session_service
)

# --- 6. Run the LinkedIn Post Generator ---
print("=== LinkedIn Post Generator with Automated Review ===")
print("Generating and refining a LinkedIn post about the ADK tutorial...")
print("The post will be automatically reviewed and refined up to 5 times.")
print(
    "Process will stop when quality requirements are met or max iterations reached.\n"
)

user_query = "Generate a LinkedIn post about what I've learned from @aiwithbrandon's Agent Development Kit tutorial."
content = types.Content(role="user", parts=[types.Part(text=user_query)])
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

# Process events to show refinement progress
for event in events:
    try:
        # Display post content from generator
        if (
            event.author == "LinkedInPostGenerator"
            and hasattr(event, "content")
            and event.content
            and event.content.parts
            and len(event.content.parts) > 0
        ):
            print("\n=== Generated Post ===")
            print(event.content.parts[0].text)
            print("=====================\n")

        # Display review results
        elif (
            event.author == "PostReviewer"
            and hasattr(event, "content")
            and event.content
            and event.content.parts
            and len(event.content.parts) > 0
        ):
            print(f"Review Result: {event.content.parts[0].text}")
            if event.content.parts[0].text == "fail":
                session = runner.session_service.get_session(
                    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
                )
                if session and hasattr(session, "state"):
                    print(f"Feedback: {session.state.get('review_feedback', 'None')}\n")

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        continue

# Get and display the final state
session = runner.session_service.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

if session and hasattr(session, "state"):
    final_post = session.state.get("current_post", "")
    print("\n----------- FINAL RESULTS -----------")
    print(f"Review Status: {session.state.get('review_status', 'None')}")
    if session.state.get("review_status") == "fail":
        print(f"Final Feedback: {session.state.get('review_feedback', 'None')}")
    print(f"\nFinal Post ({len(final_post)} characters):")
    print("=====================================")
    print(final_post)
    print("=====================================\n")
