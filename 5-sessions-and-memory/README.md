# Sessions and Memory Management in ADK

This example demonstrates how to create and manage stateful sessions in the Agent Development Kit (ADK), enabling your agents to maintain context and remember user information across interactions.

## What Are Sessions in ADK?

Sessions in ADK provide a way to:

1. **Maintain State**: Store and access user data, preferences, and other information between interactions
2. **Track Conversation History**: Automatically record and retrieve message history
3. **Personalize Responses**: Use stored information to create more contextual and personalized agent experiences

Unlike simple conversational agents that forget previous interactions, stateful agents can build relationships with users over time by remembering important details and preferences.

## Examples in This Directory

This directory contains two main examples and two agent implementations:

1. **Basic Stateful Session** (`1_basic_stateful_session.py`)
   - Demonstrates how to create a session with user preferences
   - Shows how to *retrieve information* from session state
   - Uses the `question_answering_agent` that responds based on stored user preferences

2. **Managing Stateful Sessions** (`2_manange_stateful_session.py`)
   - Shows more advanced session management
   - Demonstrates *updating session state* with new information
   - Uses the `stock_agent` to track stocks of interest and update information

3. **Agent Implementations**
   - `question_answering_agent`: Simple agent that answers questions based on user profile
   - `stock_agent`: More complex agent that fetches stock prices and maintains that data in the session

## Getting Started

### Setup Environment

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
# macOS/Linux
source .venv/bin/activate
# Windows CMD
.venv\Scripts\activate.bat
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

## Running the Examples

### Basic Stateful Session

Run the first example to see a simple stateful session in action:

```bash
python 1_basic_stateful_session.py
```

This example shows how to:
- Create a session with initial user information
- Pass that information to the agent
- Ask questions about the user's preferences

### Managing Stateful Sessions

Run the second example to see more advanced session management:

```bash
python 2_manange_stateful_session.py
```

This example demonstrates:
- Creating a session with initial stock preferences
- Using a custom tool to fetch real-time stock prices
- Updating session state with the latest information
- Examining the final state and conversation history

## Key Concepts

### InMemorySessionService

The examples use the `InMemorySessionService` which stores sessions in memory. In production applications, you might want to use a persistent storage solution.

```python
session_service = InMemorySessionService()
```

### Creating Sessions

Sessions are created with a unique identifier and initial state:

```python
session = session_service.create_session(
    app_name="MyApp",
    user_id="user123",
    session_id=str(uuid.uuid4()),
    state=initial_state,
)
```

### Using Sessions with Runners

Sessions are integrated with the `Runner` to maintain state between interactions:

```python
runner = Runner(
    agent=my_agent,
    app_name="MyApp",
    session_service=session_service,
)
```

### Accessing and Updating State

Agents can access session state using context variables in their instructions:

```
Here are the stocks of interest for the user {user_name}:
{stocks_of_interest}
```

Tools can update session state using the `tool_context`:

```python
tool_context.state["last_stock_update"] = current_time
```

## Additional Resources

- [Google ADK Sessions Documentation](https://google.github.io/adk-docs/)
- [Running Agents with Sessions](https://google.github.io/adk-docs/guides/sessions/)
- [Working with State in ADK](https://google.github.io/adk-docs/tutorials/state/)
