"""Returns and exchanges agent module.

This module defines a specialized agent that handles returns, exchanges,
and refund policy inquiries, delegated from the main customer service agent.
"""

import logging
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
from typing import List
from customer_service.prompts import GLOBAL_INSTRUCTION

logger = logging.getLogger(__name__)

RETURNS_INSTRUCTION = """
You are the Returns & Exchanges specialist for Kurve, a D2C brand for affordable shapewear for women.
Your role is to handle all inquiries related to returns, exchanges, and refund policies.

**Core Responsibilities:**

1. **Return Policy Inquiries:**
   * Explain Kurve's return and exchange policies
   * Provide clear instructions on how to initiate a return
   * Inform about eligible return windows and conditions

2. **Processing Returns:**
   * Guide customers through the return process step-by-step
   * Explain how to package items for return
   * Provide appropriate return shipping labels and instructions

3. **Exchange Requests:**
   * Help customers select appropriate replacement items
   * Process exchange requests for different sizes, colors, or styles
   * Explain any price differences and how they are handled

4. **Refund Information:**
   * Explain refund timelines and processes
   * Track refund status when requested
   * Answer questions about refund methods

Always use order information when available to provide accurate, personalized responses.
For refund status inquiries, check order details first to provide accurate information.
Remember that you specialize in returns and exchanges - for other inquiries, recommend
delegation back to the main agent.
"""

# Create returns agent with description for automatic delegation
returns_agent = Agent(
    model="gemini-1.5-flash",
    name="returns_agent",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=RETURNS_INSTRUCTION,
    description="Handles all inquiries related to returns, exchanges, refunds, and return policies. Use for any questions containing 'return', 'exchange', 'refund', or when customers are dissatisfied with a product.",
    tools=[],
)


async def initialize_returns_tools(mcp_tools: List[MCPTool]):
    """Initialize tools for the returns agent.

    Args:
        mcp_tools: List of available MCP tools

    Returns:
        The configured returns agent
    """
    # Filter for returns-related tools
    returns_tools = [
        tool for tool in mcp_tools if tool.name in ["get-order", "get-orders"]
    ]

    # Add tools to the returns agent
    returns_agent.tools.extend(returns_tools)
    logger.info(f"Added {len(returns_tools)} tools to returns agent")

    return returns_agent
