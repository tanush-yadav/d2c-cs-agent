import logging
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
from typing import List
from customer_service.prompts import GLOBAL_INSTRUCTION

logger = logging.getLogger(__name__)

ORDER_INSTRUCTION = """
You are the Order Processing specialist for Kurve. Handle all order-related inquiries with these specific steps:

**When a customer asks about an order:**

1. **If they provide what they think is an order ID (like "1579"):**
   - FIRST call get_orders(first=10, query="customer_id:CUSTOMER_ID") to retrieve recent orders
   - Look for a matching order name/number in the results (not the internal order ID)
   - If found, extract the ACTUAL order ID from the matching order
   - THEN call get_order(order_id) with the correct internal ID
   - This handles the case where customers use the customer-facing order number

2. **If they don't provide an ID:**
   - Call get_orders(first=10, query="customer_id:CUSTOMER_ID")
   - If exactly one order is found, confirm with the customer
   - If multiple orders, help them identify which one they're looking for

Function calling :
* get-orders: {'first': {'description': 'Limit of orders to return', 'type': <Type.NUMBER: 'NUMBER'>}, 'after': {'description': 'Next page cursor', 'type': <Type.STRING: 'STRING'>}, 'query': {'description': 'Filter orders using query syntax', 'type': <Type.STRING: 'STRING'>}, 'sortKey': {'description': 'Field to sort by', 'enum': ['PROCESSED_AT', 'TOTAL_PRICE', 'ID', 'CREATED_AT', 'UPDATED_AT', 'ORDER_NUMBER'], 'type': <Type.STRING: 'STRING'>}, 'reverse': {'description': 'Reverse sort order', 'type': <Type.BOOLEAN: 'BOOLEAN'>}} -> None*   `get-orders(first: int, query: str) -> dict`: Retrieves a list of orders for the current customer with query customer_id=CUSTOMER_ID
* get-order: {'orderIdentifier': {'description': "ID or number of the order to retrieve (e.g., '123456789' or '#1579')", 'type': <Type.STRING: 'STRING'>}} -> None

Always execute the actual API calls - do not describe what you would do.
Format responses clearly, including tracking information when available.
"""

# Create order agent with a description for automatic delegation
order_agent = Agent(
    model="gemini-2.0-flash",
    name="order_agent",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=ORDER_INSTRUCTION,
    tools=[],
)


async def initialize_order_tools(mcp_tools: List[MCPTool]):
    """Add order tools to the order agent and return the configured agent."""
    # Filter order tools
    order_tools = [
        tool for tool in mcp_tools if tool.name in ["get-order", "get-orders"]
    ]

    # Add tools to the order agent
    order_agent.tools.extend(order_tools)
    logger.info(f"Added {len(order_tools)} order-related tools to order agent")

    return order_agent
