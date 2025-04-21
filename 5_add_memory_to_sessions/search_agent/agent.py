import uuid

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService

# Create a NEW session service instance for this state demonstration
session_service_stateful = InMemorySessionService()


# Create a NEW session
app_name = "greeting_agent"
user_id = "brandon_hancock"
session_id = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
)
print("CREATED NEW SESSION:")
print(f"\tSession ID: {session_id}")
print(f"\tInitial State: {initial_state}")

# Create the root agent
root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="Greeting agent",
    instruction="""
    You are a helpful assistant that greets the user. Ask for the user's name and greet them by name.
    """,
)

runner = 
