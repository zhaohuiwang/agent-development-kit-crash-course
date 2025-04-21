from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import google_search

# Built in tools:
# Google Search, Code Execution, Vertex AI Search
#   More info here: https://google.github.io/adk-docs/tools/built-in-tools/#available-built-in-tools
# Important Note: Currently, for each root agent or single agent, only one built-in tool is supported.
#   More info here: https://google.github.io/adk-docs/tools/built-in-tools/#use-built-in-tools-with-other-tools


# Custom Function Tool Best Practices:
# https://google.github.io/adk-docs/tools/function-tools/#1-function-tool
# Parameters:
#   Define your function parameters using standard JSON-serializable types (e.g., string, integer, list, dictionary)
#   DO NOT USE DEFAULT VALUES - not currently supported in ADK
# Return Type:
#   The preferred return type for a Python Function Tool is a dictionary
#   If you don't return a dictionary, ADK will wrap it into a dictionary {"result": ...}
#   Strive to make your return values as descriptive as possible. Best practice:
#   {"status": "success", "error_message": None, "result": "..."}
# Doc String:
#   The docstring of your function serves as the tool's description and is sent to the LLM.
#   Focus on clarity so that the LLM can understand how to use the tool effectively.


# def get_current_time() -> dict:
#     """
#     Get the current time in the format YYYY-MM-DD HH:MM:SS
#     """
#     return {
#         "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction="""
    You are a helpful assistant that can use the following tools:
    - google_search
    """,
    tools=[google_search],
    # tools=[get_current_time],
    # tools=[google_search, get_current_time], # <--- Doesn't work
)
