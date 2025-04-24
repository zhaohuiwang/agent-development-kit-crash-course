# Multi-Agent System Example

## What is a Multi-Agent System?

A Multi-Agent System is an advanced pattern in the Agent Development Kit (ADK) that allows multiple specialized agents to work together to handle complex tasks. Each agent can focus on a specific domain or functionality, and they can collaborate through delegation and communication to solve problems that would be difficult for a single agent.

## Key Components

### 1. Root Agent
The root agent acts as the main coordinator, receiving user queries and deciding which specialized agent should handle each request. It can be configured with:
- A routing logic based on agent descriptions
- Direct access to sub-agents for delegation
- A set of tools including agent tools for specialized tasks

### 2. Sub-Agents
Sub-agents are specialized agents that focus on specific domains or tasks:
- Each can have its own model, instructions, and tools
- They can be designed for specific knowledge domains
- They receive delegated tasks from the root agent

### 3. Agent Tools
Agent tools allow one agent to use another agent as a tool, enabling complex collaboration patterns.

## Limitations When Using Multi-Agents

### Sub-agent Restrictions

**Built-in tools cannot be used within a sub-agent.**

For example, this approach using built-in tools within sub-agents is **not** currently supported:

```python
search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="You're a specialist in Google Search",
    tools=[google_search],
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="You're a specialist in Code Execution",
    tools=[built_in_code_execution],
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    sub_agents=[
        search_agent,  # NOT SUPPORTED
        coding_agent   # NOT SUPPORTED
    ],
)
```

### Workaround Using Agent Tools

To use multiple built-in tools or to combine built-in tools with other tools, you can use the `AgentTool` approach:

```python
from google.adk.tools import agent_tool

search_agent = Agent(
    model='gemini-2.0-flash',
    name='SearchAgent',
    instruction="You're a specialist in Google Search",
    tools=[google_search],
)
coding_agent = Agent(
    model='gemini-2.0-flash',
    name='CodeAgent',
    instruction="You're a specialist in Code Execution",
    tools=[built_in_code_execution],
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Root Agent",
    tools=[
        agent_tool.AgentTool(agent=search_agent), 
        agent_tool.AgentTool(agent=coding_agent)
    ],
)
```

This approach wraps agents as tools, allowing the root agent to delegate to specialized agents that each use a single built-in tool.

## Implementation Example

The multi-agent example demonstrates how to create a system with multiple specialized agents that can handle different types of queries. The manager agent routes requests to the appropriate specialized agent based on the query content.

## Getting Started

This example uses the same virtual environment created in the root directory. Make sure you have:

1. Activated the virtual environment from the root directory:
```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

2. Set up your API key:
   - Rename `.env.example` to `.env` in the manager folder
   - Add your Google API key to the `GOOGLE_API_KEY` variable in the `.env` file

## Running the Example

To run the multi-agent example:

1. Navigate to the 6-multi-agent directory containing your agent folders.

2. Start the interactive web UI:
```bash
adk web
```

3. Access the web UI by opening the URL shown in your terminal (typically http://localhost:8000)

4. Select the "manager" agent from the dropdown menu in the top-left corner of the UI

5. Start chatting with your agent in the textbox at the bottom of the screen

### Example Prompts to Try

- "Can you tell me about the stock market today?"
- "Tell me something funny about programming"
- "What's the latest tech news?"

You can exit the conversation or stop the server by pressing `Ctrl+C` in your terminal.

## Additional Resources

- [ADK Multi-Agent Systems Documentation](https://google.github.io/adk-docs/agents/multi-agent-systems/) 
