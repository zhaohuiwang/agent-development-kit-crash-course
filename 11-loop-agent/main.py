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
from tools import get_human_feedback

load_dotenv()

# Pattern: Human-in-the-Loop Iterative Refinement

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

    Your task is to create or revise an engaging LinkedIn post about an Agent Development Kit (ADK) tutorial by @aiwithbrandon.
    
    ## STEP 1: DETERMINE ACTION BASED ON FEEDBACK STATUS
    - If state['feedback_status'] is 'approved': No action needed. Return the current post without changes.
    - If state['feedback_status'] is 'initial': Create a new post from scratch (see INITIAL POST GUIDELINES).
    - If state['feedback_status'] is 'revise': Modify the existing post based on feedback (see REVISION GUIDELINES).
    
    ## STEP 2: FOLLOW ACTION-SPECIFIC GUIDELINES
    
    ### INITIAL POST GUIDELINES
    When creating a new post, include:
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
    6. After creating the post, save the new post to state['current_post'].
    
    ### REVISION GUIDELINES
    When revising an existing post:
    1. Read state['current_post'] - this is what you're modifying
    2. Read state['feedback_content'] - this is what to change
    3. Apply the feedback PRECISELY and LITERALLY.
    4. Do not add features not requested
    5. Do not explain your changes
    6. After revising the post, save the revised post to state['current_post'].
    
    """,
    description="Generates or refines LinkedIn posts based on feedback",
    output_key="current_post",
)

# --- 2. Define the Feedback Processing Agent ---
feedback_processor = LlmAgent(
    name="FeedbackProcessor",
    model=GEMINI_MODEL,
    instruction="""You are a Feedback Analyzer.
    
    Your primary job is to use the get_human_feedback tool to collect feedback.
    
    PROCESS:
    1. Call the get_human_feedback tool
    2. After calling the tool, return ONLY the text "Feedback received" - nothing more
    
    The tool will directly update the state with:
    - feedback_status
    - feedback_content
    
    DO NOT analyze or respond to the feedback content.
    DO NOT add any additional text beyond "Feedback received".
    DO NOT engage in conversation with the user.
    """,
    tools=[get_human_feedback],
    output_key="feedback_summary",
)


# --- 3. Define a custom EscalationAgent to determine if the loop should continue ---
class FeedbackEscalationAgent(BaseAgent):
    """
    Checks feedback status and determines if the loop should continue or escalate.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # Get the feedback status directly from the state
        feedback_status = ctx.session.state.get("feedback_status", "revise")

        # Escalate (stop the loop) if approved
        should_stop = feedback_status == "approved"

        # Create and yield the event with escalation decision
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


# --- 4. Create the LoopAgent for iterative refinement ---
linkedin_post_loop = LoopAgent(
    name="LinkedInPostRefinementLoop",
    max_iterations=5,  # Maximum 5 rounds of feedback
    sub_agents=[
        post_generator,
        feedback_processor,
        FeedbackEscalationAgent(name="ContinuationDecider"),
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
print("=== LinkedIn Post Generator with Human-in-the-Loop Refinement ===")
print(
    "This system will generate a LinkedIn post about learning from @aiwithbrandon's ADK tutorial."
)
print("You'll be able to provide feedback and refine the post up to 5 times.")
print("Type 'approve' when you're satisfied, or 'restart' to begin again.\n")

user_query = "Generate a LinkedIn post about what I've learned from @aiwithbrandon's Agent Development Kit tutorial."

content = types.Content(role="user", parts=[types.Part(text=user_query)])
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

for event in events:
    try:

        # For the final response (after approval)
        if event.is_final_response():

            # Get the final approved post from the session state
            final_post = ""
            try:
                session = runner.session_service.get_session(
                    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
                )
                if session and hasattr(session, "state"):
                    final_post = session.state.get("current_post", "")
                    print("\n----------- FINAL STATE DEBUG -----------")
                    print(
                        f"Final feedback_status: {session.state.get('feedback_status', 'None')}"
                    )
                    print(
                        f"Final feedback_content: {session.state.get('feedback_content', 'None')}"
                    )
                    print(f"Final current_post length: {len(final_post)} chars")
                    print("----------------------------------\n")
            except Exception as e:
                print(f"Error accessing session state: {str(e)}")

    except Exception as e:
        # Safely handle any unexpected event structure
        print(f"Error handling event: {str(e)}")
        continue


session = runner.session_service.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

if session and hasattr(session, "state"):
    final_post = session.state.get("current_post", "")
    print("\n----------- FINAL STATE DEBUG -----------")
    print(f"Final feedback_status: {session.state.get('feedback_status', 'None')}")
    print(f"Final feedback_content: {session.state.get('feedback_content', 'None')}")
    print(f"Final current_post length: {len(final_post)} chars")
    print("----------------------------------\n")
