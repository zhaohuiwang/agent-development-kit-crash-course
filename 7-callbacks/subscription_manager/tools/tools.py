from datetime import datetime
from typing import Dict

from google.adk.tools.tool_context import ToolContext

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
