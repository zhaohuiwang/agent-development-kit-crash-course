from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Pattern: Sequential Pipeline Pattern

# --- Constants ---
APP_NAME = "lead_qualification_app"
USER_ID = "aiwithbrandon"
SESSION_ID = "qualification_session_01"
GEMINI_MODEL = "gemini-2.0-flash"

# --- 1. Define Sub-Agents for Lead Qualification Pipeline ---

# Lead Data Validator Agent
# Validates the incoming lead data to ensure it has all necessary information
lead_validator_agent = LlmAgent(
    name="LeadValidatorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Lead Validation AI.
    
    Examine the lead information provided by the user and determine if it's complete enough for qualification.
    A complete lead should include:
    - Contact information (name, email or phone)
    - Some indication of interest or need
    - Company or context information if applicable
    
    Output ONLY 'valid' or 'invalid' with a single reason if invalid.
    
    Example valid output: 'valid'
    Example invalid output: 'invalid: missing contact information'
    """,
    description="Validates lead information for completeness.",
    # Stores validation status in session state
    output_key="validation_status",
)

# Lead Scorer Agent
# Scores the lead based on qualification criteria
lead_scorer_agent = LlmAgent(
    name="LeadScorerAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Lead Scoring AI.
    
    First, check the 'validation_status' in the session state. Only proceed if it's 'valid'.
    
    Analyze the lead information and assign a qualification score from 1-10 based on:
    - Expressed need (urgency/clarity of problem)
    - Decision-making authority
    - Budget indicators
    - Timeline indicators
    
    Output ONLY a numeric score and ONE sentence justification.
    
    Example output: '8: Decision maker with clear budget and immediate need'
    Example output: '3: Vague interest with no timeline or budget mentioned'
    """,
    description="Scores qualified leads on a scale of 1-10.",
    # Stores score and justification in session state
    output_key="lead_score",
)

# Action Recommender Agent
# Recommends next steps based on lead score
action_recommender_agent = LlmAgent(
    name="ActionRecommenderAgent",
    model=GEMINI_MODEL,
    instruction="""You are an Action Recommendation AI.
    
    Read the 'validation_status' and 'lead_score' from the session state.
    
    Based on this information, recommend the appropriate next steps:
    
    - For invalid leads: Suggest what additional information is needed
    - For leads scored 1-3: Suggest nurturing actions (educational content, etc.)
    - For leads scored 4-7: Suggest qualifying actions (discovery call, needs assessment)
    - For leads scored 8-10: Suggest sales actions (demo, proposal, etc.)
    
    Format your response as a complete recommendation to the sales team.
    """,
    description="Recommends next actions based on lead qualification.",
    # No output_key as this is the final output of the pipeline
)

# --- 2. Create the SequentialAgent ---
lead_qualification_pipeline = SequentialAgent(
    name="LeadQualificationPipeline",
    sub_agents=[lead_validator_agent, lead_scorer_agent, action_recommender_agent],
    # Pipeline flow: Validator -> Scorer -> Recommender
)

# --- 3. Setup Session and Runner ---
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=lead_qualification_pipeline,
    app_name=APP_NAME,
    session_service=session_service,
)

# --- 4. Example Lead Information ---
# Qualified lead example (high-quality lead)
# example_lead = """
# Lead Information:
# Name: Sarah Johnson
# Email: sarah.j@techinnovate.com
# Phone: 555-123-4567
# Company: Tech Innovate Solutions
# Position: CTO
# Interest: Looking for an AI solution to automate customer support
# Budget: $50K-100K available for the right solution
# Timeline: Hoping to implement within next quarter
# Notes: Currently using a competitor's product but unhappy with performance
# """

# Unqualified lead example - uncomment this and comment the above example to test
example_lead = """
Lead Information:
Name: John Doe
Email: john@gmail.com
Interest: Something with AI maybe
Notes: Met at conference, seemed interested but was vague about needs
"""

# --- 5. Process Lead ---
print("Processing lead through qualification pipeline...")
content = types.Content(role="user", parts=[types.Part(text=example_lead)])
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

# Process and display results
for event in events:
    if event.is_final_response() and event.content and event.content.parts:
        final_response = event.content.parts[0].text
        print("\n=== LEAD QUALIFICATION RESULT ===")
        print(final_response)
        print("================================\n")
