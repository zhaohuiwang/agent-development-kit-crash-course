from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="Google search agent",
    instruction="""
    You are a helpful assistant that can search the web using Google search.
    """,
    tools=[google_search],
)
