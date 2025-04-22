import json
import re
from datetime import datetime
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# ------------------------
# Mock Database Operations
# ------------------------

# Simulated user database
SUBSCRIPTION_DB = {
    "user123": {
        "user_id": "user123",
        "name": "Alice Johnson",
        "subscription_status": "active",
        "subscription_tier": "premium",
        "last_payment_date": "2024-03-15",
        "next_billing_date": "2024-04-15",
        "payment_method": "Visa ending in 4242",
        "payment_history": [
            {"date": "2024-03-15", "amount": 19.99, "status": "successful"},
            {"date": "2024-02-15", "amount": 19.99, "status": "successful"},
            {"date": "2024-01-15", "amount": 19.99, "status": "successful"},
        ],
    },
    "user456": {
        "user_id": "user456",
        "name": "Bob Smith",
        "subscription_status": "cancelled",
        "subscription_tier": "basic",
        "last_payment_date": "2024-02-10",
        "next_billing_date": None,
        "payment_method": "MasterCard ending in 5555",
        "payment_history": [
            {"date": "2024-02-10", "amount": 9.99, "status": "successful"},
            {"date": "2024-01-10", "amount": 9.99, "status": "successful"},
            {"date": "2023-12-10", "amount": 9.99, "status": "successful"},
            {"date": "2023-11-10", "amount": 9.99, "status": "successful"},
        ],
    },
    "user789": {
        "user_id": "user789",
        "name": "Charlie Davis",
        "subscription_status": "trial",
        "subscription_tier": "premium",
        "last_payment_date": None,
        "next_billing_date": "2024-04-30",
        "payment_method": "PayPal",
        "payment_history": [],
    },
}


def get_user_info(user_id: str) -> Dict:
    """Simulates fetching user subscription information from a database."""
    if user_id in SUBSCRIPTION_DB:
        return SUBSCRIPTION_DB[user_id]
    else:
        # Return minimal default info for new users
        return {
            "user_id": user_id,
            "subscription_status": "none",
            "last_payment_date": None,
            "payment_history": [],
        }


def update_user_subscription(user_id: str, new_status: str) -> Dict:
    """Simulates updating a user's subscription status in the database."""
    if user_id not in SUBSCRIPTION_DB:
        SUBSCRIPTION_DB[user_id] = {
            "user_id": user_id,
            "subscription_status": "none",
            "last_payment_date": None,
            "payment_history": [],
        }

    user_info = SUBSCRIPTION_DB[user_id]
    current_time = datetime.now().strftime("%Y-%m-%d")

    # Update subscription info based on new status
    user_info["subscription_status"] = new_status

    if new_status == "active":
        user_info["subscription_tier"] = user_info.get("subscription_tier", "basic")
        user_info["last_payment_date"] = current_time
        user_info["next_billing_date"] = "2024-05-15"  # Example date

        # Add new payment to history
        if "payment_history" not in user_info:
            user_info["payment_history"] = []

        payment_amount = 19.99 if user_info["subscription_tier"] == "premium" else 9.99
        user_info["payment_history"].append(
            {"date": current_time, "amount": payment_amount, "status": "successful"}
        )

    elif new_status == "cancelled":
        user_info["next_billing_date"] = None

    # Update in our mock database
    SUBSCRIPTION_DB[user_id] = user_info

    return user_info


# ------------------------
# Subscription Tools
# ------------------------


def change_subscription_status(tool_context: ToolContext) -> Dict:
    """
    Changes a user's subscription status.

    Args:
        new_status: The new subscription status ("active", "cancelled", "trial", "paused")
    """
    # Extract arguments safely
    tool_args = tool_context.args or {}
    new_status = tool_args.get("new_status", "").lower()

    # Validate arguments
    valid_statuses = ["active", "cancelled", "trial", "paused"]
    if new_status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}",
        }

    # Get user_id from context
    user_id = tool_context.state.get("user_id")
    if not user_id:
        return {"success": False, "error": "User ID not found in session state"}

    # Update subscription
    updated_info = update_user_subscription(user_id, new_status)

    return {
        "success": True,
        "user_id": user_id,
        "old_status": tool_context.state.get("subscription_status", "unknown"),
        "new_status": new_status,
        "message": f"Subscription status changed to {new_status}",
    }


# ------------------------
# Agent Callbacks
# ------------------------


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Before agent callback: Hydrates state with user subscription data.
    This mimics fetching data from a database when the agent is invoked.
    """
    print("[Callback] Executing before_agent_callback")

    # Get session state
    state = callback_context.state

    # Check if we have user_id in state
    user_id = state.get("user_id")
    if not user_id:
        print("[Callback] No user_id found in state, using default")
        user_id = "user123"  # Default for demonstration
        state["user_id"] = user_id

    # Fetch detailed user info (in a real system, this would query a database)
    print(f"[Callback] Fetching subscription info for user: {user_id}")
    user_info = get_user_info(user_id)

    # Update state with fetched data
    for key, value in user_info.items():
        if key != "user_id":  # We already have user_id
            state[key] = value

    print(
        f"[Callback] State hydrated with subscription data: {json.dumps(state, default=str)}"
    )

    # Return None to continue with normal agent execution
    return None


def after_agent_callback(
    callback_context: CallbackContext, response: types.Content
) -> Optional[types.Content]:
    """
    After agent callback: Updates state with interaction details.
    """
    print("[Callback] Executing after_agent_callback")

    # Get session state
    state = callback_context.state

    # Record the interaction in state
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract the response text
    response_text = ""
    if response and hasattr(response, "parts") and response.parts:
        response_text = (
            response.parts[0].text if hasattr(response.parts[0], "text") else ""
        )

    # Update state with interaction details
    state["last_interaction"] = {
        "time": current_time,
        "message": (
            response_text[:100] + "..."
            if response_text and len(response_text) > 100
            else response_text
        ),
    }

    print(f"[Callback] Updated state with interaction details at {current_time}")

    # Return None to use the original response
    return None


def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Before model callback: Checks for profanity and blocks requests if found.
    """
    print("[Callback] Executing before_model_callback")

    # Get the last user message
    last_user_message = ""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        if llm_request.contents[-1].parts:
            last_user_message = llm_request.contents[-1].parts[0].text or ""

    print(f"[Callback] Checking user message: '{last_user_message}'")

    # Check for profanity - in this example we're just checking for the word "SUCK"
    if "SUCK" in last_user_message.upper():
        print("[Callback] Profanity detected, blocking LLM call")

        # Return a response to skip the LLM call
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="I can't help you when you're using language like that. Please rephrase your question respectfully."
                    )
                ],
            )
        )

    # No profanity detected, proceed with the LLM call
    print("[Callback] No profanity detected, proceeding with LLM call")
    return None


def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """
    After model callback: Replace "AI assistant" with "Brandon Bot" in responses.
    """
    print("[Callback] Executing after_model_callback")

    # Check if there is a response with text content
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        print("[Callback] No content in LLM response to modify")
        return None

    # Get the original response text
    original_text = llm_response.content.parts[0].text or ""

    # Replace "AI assistant" with "Brandon Bot" (case insensitive)
    modified_text = re.sub(r"(?i)AI assistant", "Brandon Bot", original_text)

    # If changes were made, create a new response
    if modified_text != original_text:
        print("[Callback] Replaced 'AI assistant' with 'Brandon Bot' in response")

        # Create a copy of the original response
        new_content = types.Content(
            role=llm_response.content.role, parts=[types.Part(text=modified_text)]
        )

        new_response = LlmResponse(content=new_content)
        return new_response

    # No changes needed
    print("[Callback] No replacements needed in response")
    return None


def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    Before tool callback: Verify that the user_id in the tool context matches the session state.
    """
    print(f"[Callback] Executing before_tool_callback for tool: {tool.name}")

    # Get user_id from state
    state_user_id = context.state.get("user_id")

    if not state_user_id:
        print("[Callback] No user_id found in state, blocking tool execution")
        return {"success": False, "error": "Unauthorized: No user ID in session"}

    print(f"[Callback] Verifying tool access for user: {state_user_id}")

    # In a real system, you might check permissions here
    # For this example, we'll just validate the user exists in our DB
    if state_user_id not in SUBSCRIPTION_DB:
        print(f"[Callback] User {state_user_id} not found in database")
        return {
            "success": False,
            "error": f"Unauthorized: User {state_user_id} not found",
        }

    # Add request timestamp to tool arguments for logging
    # Note: We don't modify the original, but rather return a new dict
    enriched_args = args.copy()
    enriched_args["_request_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"[Callback] Tool access verified for user {state_user_id}, proceeding with enriched arguments"
    )

    # Return the enriched arguments to be used by the tool
    return enriched_args


def after_tool_callback(
    tool: BaseTool, result: Dict[str, Any], context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    After tool callback: Adds additional information to tool responses.
    """
    print(f"[Callback] Executing after_tool_callback for tool: {tool.name}")

    # Create a copy of the response to avoid modifying the original
    enhanced_response = result.copy()

    # Add processing timestamp
    enhanced_response["_processed_timestamp"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Add a friendly message based on subscription status change if applicable
    if (
        tool.name == "change_subscription_status"
        and enhanced_response.get("success") == True
    ):
        new_status = enhanced_response.get("new_status")

        if new_status == "active":
            enhanced_response["friendly_message"] = (
                "Welcome to our subscription service! You now have full access to all premium features."
            )
        elif new_status == "cancelled":
            enhanced_response["friendly_message"] = (
                "We're sorry to see you go. Your subscription has been cancelled, but you'll have access until the end of your billing period."
            )
        elif new_status == "paused":
            enhanced_response["friendly_message"] = (
                "Your subscription is now paused. You can resume it anytime."
            )
        elif new_status == "trial":
            enhanced_response["friendly_message"] = (
                "Enjoy your trial period! You'll have access to all premium features for the next 14 days."
            )

    print(f"[Callback] Enhanced tool response with additional information")

    return enhanced_response


# ------------------------
# Create the Agent
# ------------------------

subscription_manager = LlmAgent(
    name="subscription_manager",
    model="gemini-2.0-flash",
    description="Subscription manager agent with callbacks",
    instruction="""
    You are a helpful subscription management assistant that helps users understand and manage their subscription.
    
    You can provide information about:
    - Current subscription status
    - Billing details and payment history
    - Next billing date
    - Subscription options
    
    You can also help users change their subscription status using the change_subscription_status tool.
    
    The available subscription statuses are:
    - active: An active paid subscription
    - cancelled: A subscription that has been cancelled
    - paused: A temporarily paused subscription
    - trial: A free trial subscription
    
    Always be professional, helpful, and clear in your explanations.
    
    User's Current Subscription Information:
    - User ID: {user_id}
    - Name: {name} (if available)
    - Status: {subscription_status}
    - Tier: {subscription_tier} (if applicable)
    - Last Payment: {last_payment_date}
    - Next Billing: {next_billing_date}
    - Payment Method: {payment_method}
    
    Payment History:
    {payment_history}
    """,
    tools=[change_subscription_status],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
