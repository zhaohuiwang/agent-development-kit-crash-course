from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.funny_nerd.agent import funny_nerd
from .sub_agents.news_analyst.agent import news_analyst
from .sub_agents.stock_analyst.agent import stock_analyst


def get_current_time() -> dict:
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - stock_analyst
    - funny_nerd

    You also have access to the following tools:
    - news_analyst
    """,
    # Sub Agents
    # Once the root agent delegates to the sub agent, the sub agent takes over
    # the entire response.
    # Limitations: https://google.github.io/adk-docs/tools/built-in-tools/#limitations
    # Built-in tools cannot be used within a sub-agent.
    sub_agents=[stock_analyst, funny_nerd],
    #
    #
    # Option 2: Treat Agents as Tools
    # The root agent can delegate to the sub agent, and the sub agent will
    # return a response to the root agent, which will then be used in
    # the root agent response.
    # Agent-as-a-tool: https://google.github.io/adk-docs/tools/function-tools/#3-agent-as-a-tool
    tools=[
        AgentTool(news_analyst),
        get_current_time,
    ],
)
