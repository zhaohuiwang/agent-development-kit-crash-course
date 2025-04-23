# Simple Memory Agent with SQLite Database

This project demonstrates how to create a simple agent with persistent memory using Google ADK's DatabaseSessionService with SQLite. The agent remembers the user's name and conversation history across different sessions.

## Prerequisites

- Python 3.9+
- Google API key for Gemini models

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Add your Google API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Project Structure

- `main.py`: Contains the agent definition, database setup, and conversation loop
- `.env`: Configuration file for API keys
- `my_agent_data.db`: SQLite database that gets created when the agent runs

## Running the Agent

1. Make sure your API key is set in the `.env` file
2. Run the application:
   ```
   python main.py
   ```
3. Interact with the agent in the terminal
4. The agent will remember your name and conversation history across sessions

## Features

- Simple agent that demonstrates persistent storage
- Remembers user's name and conversation history
- Continues conversations seamlessly across different sessions
- Uses SQLite database for persistent storage

## How It Works

The agent uses the `DatabaseSessionService` from Google ADK to store session information in an SQLite database. When the application starts, it checks for existing sessions and either continues the most recent one or creates a new session if none exists.

The agent's state includes:
- User name
- Conversation history (limited to the last 10 messages)

This information persists between conversations, allowing the agent to provide a personalized experience. 
