from datetime import datetime

import yfinance as yf
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext


def get_stock_price(ticker: str, tool_context: ToolContext) -> dict:
    """Retrieves current stock price and saves to session state."""
    print(f"--- Tool: get_stock_price called for {ticker} ---")

    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        current_price = stock.info.get("currentPrice")

        if current_price is None:
            return {
                "status": "error",
                "error_message": f"Could not fetch price for {ticker}",
            }

        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tool_context.state["last_stock_update"] = current_time

        return {
            "status": "success",
            "ticker": ticker,
            "price": current_price,
            "timestamp": current_time,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error fetching stock data: {str(e)}",
        }


# Create the root agent
stock_agent = Agent(
    name="stock_agent",
    model="gemini-2.0-flash",
    description="An agent that can look up stock prices and track them over time.",
    instruction="""
    You are a helpful stock market assistant that helps users track their stocks of interest.
    
    The user's stocks of interest are provided in the session state under 'stocks_of_interest'.
    For example, the state might look like:
    {
        "stocks_of_interest": ["GOOG", "TSLA", "META"]
    }
    
    When asked about stock prices:
    1. Get the list of stocks from state['stocks_of_interest']
    2. Use the get_stock_price tool to fetch the latest price for each stock
    3. Format the response to show each stock's current price and the time it was fetched
    4. If a stock price couldn't be fetched, mention this in your response
    
    Example response format:
    "Here are the current prices for your stocks:
    - GOOG: $175.34 (updated at 2024-04-21 16:30:00)
    - TSLA: $156.78 (updated at 2024-04-21 16:30:00)
    - META: $123.45 (updated at 2024-04-21 16:30:00)"

    Here are the stocks of interest for the user {user_name}:
    {stocks_of_interest}
    """,
    tools=[get_stock_price],
    output_key="final_stock_response",
)
