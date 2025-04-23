import asyncio
import uuid

# Import the main customer service agent
from customer_service_agent.agent import customer_service_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from utils import add_user_query_to_history, call_agent_async

load_dotenv()

# Create a new session service to store state
session_service = InMemorySessionService()


def initialize_state():
    """Initialize the session state with default values."""
    return {
        "user_name": "Brandon Hancock",
        "purchased_courses": [""],
        "interaction_history": [],
    }


async def main_async():
    # Setup constants
    APP_NAME = "Customer Support"
    USER_ID = "aiwithbrandon"
    SESSION_ID = str(uuid.uuid4())

    # Create a new session with initial state
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initialize_state(),
    )
    print(f"Created new session: {SESSION_ID}")

    # Create a runner with the main customer service agent
    runner = Runner(
        agent=customer_service_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Interactive conversation loop
    print("\nWelcome to Customer Service Chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        # Update interaction history with the user's query
        add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    # Show final session state
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


def main():
    """Entry point for the application."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
