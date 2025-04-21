import uuid

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from stock_agent import stock_agent

load_dotenv()

# Create a new session service to store state
session_service_stateful = InMemorySessionService()

initial_state = {
    "user_name": "Brandon Hancock",
    "stocks_of_interest": ["GOOG", "TSLA", "META"],
}

# Create a NEW session
APP_NAME = "Stock Bot"
USER_ID = "brandon_hancock"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)
print("CREATED NEW SESSION:")
print(f"\tSession ID: {SESSION_ID}")

runner = Runner(
    agent=stock_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)

new_message = types.Content(
    role="user",
    parts=[
        types.Part(
            text="What are the current stock prices for each of my stocks of interest?"
        )
    ],
)

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=new_message,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"Final Response: {event.content.parts[0].text}")

session = session_service_stateful.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Showcase message history in sessions
print("Session Events:")
for event in session.events:
    if event.content and event.content.parts:
        print(event.content.parts[0].text)

# Showcase final state
print("Final State:")
print(session.state)
