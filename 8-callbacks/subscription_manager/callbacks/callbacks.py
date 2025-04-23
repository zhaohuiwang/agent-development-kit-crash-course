from google.adk.agents.callback_context import CallbackContext

from ..tools.tools import get_user_info


def check_subscription_status(callback_context: CallbackContext) -> None:
    """
    Callback function to check and update user subscription status in the LLM's context.
    This is called before the LLM processes the user's message.
    """
    # Get user ID from state or user info
    user_id = callback_context.state.get("user_id")

    # If we don't have a user ID yet, we might be in the first turn
    if not user_id:
        # For demo purposes, assign a default user
        user_id = "user123"
        callback_context.state["user_id"] = user_id

    # Get current subscription info
    user_info = get_user_info(user_id)

    # Update state with relevant subscription info
    callback_context.state["subscription_status"] = user_info["subscription_status"]
    callback_context.state["subscription_tier"] = user_info.get(
        "subscription_tier", "none"
    )

    # Add info to LLM context for personalization
    subscription_status = user_info["subscription_status"]
    subscription_tier = user_info.get("subscription_tier", "none")

    # Prepare context message for LLM
    if subscription_status == "active":
        # Replace add_message_to_history with appropriate implementation
        system_message = f"The user has an active {subscription_tier} subscription. They have full access to all features."
        callback_context.state["system_message"] = system_message
    elif subscription_status == "trial":
        # Replace add_message_to_history with appropriate implementation
        system_message = "The user is in a trial period. They have access to all premium features, but should be encouraged to upgrade before the trial ends."
        callback_context.state["system_message"] = system_message
    elif subscription_status == "cancelled":
        # Replace add_message_to_history with appropriate implementation
        system_message = "The user has cancelled their subscription. They only have access to basic features. Consider suggesting they reactivate their subscription."
        callback_context.state["system_message"] = system_message
    else:
        # Replace add_message_to_history with appropriate implementation
        system_message = "The user does not have an active subscription. They only have access to free features. Consider suggesting they start a trial or subscribe."
        callback_context.state["system_message"] = system_message
