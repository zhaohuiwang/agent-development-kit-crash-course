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
    
    If this is the first iteration (no current_post in state), create a new post that:
    1. Expresses excitement about learning from the tutorial
    2. Mentions specific aspects of ADK they learned, including:
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
    3. Contains a brief statement about how these capabilities will improve their AI applications
    4. Includes a mention/tag of @aiwithbrandon
    5. Has a clear call-to-action for connections to check out the tutorial
    
    IMPORTANT REVISION INSTRUCTIONS:
    When there is feedback in the state (feedback_status is 'revise' and feedback_content has text):
    1. Read the current_post from state - this is the post you need to modify 
    2. Read feedback_content exactly as written - this is what you need to change
    3. Apply the feedback PRECISELY:
       - If user says "no emojis" - REMOVE ALL EMOJIS
       - If user says "more professional" - Remove casual language and emoticons
       - If user says "shorter" - Reduce the length substantially
       - ALWAYS follow the feedback literally and exactly as written
    4. Do not add features the user didn't ask for
    5. Do not explain your changes or talk about the feedback
    
    The post should:
    - Be professional yet conversational
    - Be concise (ideal for LinkedIn)
    - Show enthusiasm about the subject
    - Highlight practical applications of these capabilities
    - Be ready to copy-paste into LinkedIn
    
    Output ONLY the revised post without any additional comments.
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

# Process and display results
completion_message_shown = False

for event in events:
    try:
        # Display all non-final response events with content
        if (
            not event.is_final_response()
            and hasattr(event, "content")
            and event.content
            and event.content.parts
        ):
            if len(event.content.parts) > 0 and event.content.parts[0].text:
                text = event.content.parts[0].text

                # Display only if it seems substantial (filter out very short responses)
                if len(text) > 50:
                    print("\n=== LINKEDIN POST ===")
                    print(text)
                    print("===================\n")

        # For the final response (after approval)
        if event.is_final_response() and not completion_message_shown:
            completion_message_shown = True

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

            if final_post:
                print("\n=== YOUR APPROVED LINKEDIN POST ===")
                print(final_post)
                print("==================================\n")
            else:
                print("No post found in session state")

            print(
                "Post generation complete! Copy and paste this post to LinkedIn to share your learning experience."
            )
    except Exception as e:
        # Safely handle any unexpected event structure
        print(f"Error handling event: {str(e)}")
        continue
