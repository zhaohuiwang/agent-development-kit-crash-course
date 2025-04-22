import asyncio
import uuid
from datetime import datetime

from agent import subscription_manager
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Create a new session service to store state
session_service = InMemorySessionService()


def initialize_state(user_id="user123"):
    """Initialize the session state with default values."""
    return {
        "user_id": user_id,
        # Minimal initial state - the before_agent_callback will hydrate it with user data
    }


async def main_async():
    # Setup constants
    APP_NAME = "Subscription Manager"
    USER_ID = "user123"  # Default user
    SESSION_ID = str(uuid.uuid4())

    # Create a new session with initial state
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initialize_state(USER_ID),
    )
    print(f"Created new session: {SESSION_ID}")

    # Create a runner with the subscription manager agent
    runner = Runner(
        agent=subscription_manager,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # Interactive conversation loop
    print("\nWelcome to Subscription Manager Chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    print("Special test commands:")
    print("  - Type 'switch:user456' to switch to a user with cancelled subscription")
    print("  - Type 'switch:user789' to switch to a user with trial subscription")
    print("  - Include 'SUCK' in your message to test profanity filter")
    print("  - Try using phrases with 'AI assistant' to see replacements")

    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        # Check for user switch command
        if user_input.startswith("switch:"):
            new_user_id = user_input.split(":", 1)[1].strip()
            # Create a new session for the new user
            SESSION_ID = str(uuid.uuid4())
            session_service.create_session(
                app_name=APP_NAME,
                user_id=new_user_id,
                session_id=SESSION_ID,
                state=initialize_state(new_user_id),
            )
            print(f"Switched to user: {new_user_id} (Session: {SESSION_ID})")
            continue

        # Create the message
        new_message = types.Content(role="user", parts=[types.Part(text=user_input)])

        print("\n--- Processing your request ---")

        # Run the agent
        try:
            final_response = None
            for event in runner.run(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=new_message,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text

            # For clean output formatting in the demo
            if final_response:
                print("\nAgent Response:")
                print("-" * 40)
                print(final_response)
                print("-" * 40)
        except Exception as e:
            print(f"ERROR: {e}")

    # Show final session state
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        if key == "payment_history":
            print(f"  {key}: [Payment history with {len(value)} entries]")
        else:
            print(f"  {key}: {value}")


def main():
    """Entry point for the application."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
