"""Product recommendation agent module.

This module defines a specialized agent that handles product recommendation,
identification, and selection inquiries, delegated from the main agent.
"""

import logging
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
from typing import List
from customer_service.prompts import GLOBAL_INSTRUCTION

logger = logging.getLogger(__name__)

PRODUCT_INSTRUCTION = """
You are the Product Specialist for Kurve, a D2C brand for affordable shapewear for women.
Your role is to provide expert product recommendations and help customers find the perfect products.
Before answering any questions, get the product details from the database.
If user asks about a specific product, get products, map the ID and get that specific product detail with ID.

Core Responsibilities:

1. Product Identification:
   * Help customers identify products based on their needs
   * Match customer preferences to product features
   * Suggest alternatives when preferred items are unavailable

2. Personalized Recommendations:
   * Recommend products based on customer's body type, preferences, and needs
   * Suggest complementary products that work well together
   * Provide size and fit guidance for shapewear products

3. Product Information:
   * Explain product features, materials, and benefits
   * Answer questions about product care and maintenance
   * Provide detailed information about product specifications

4. Comparison and Selection:
   * Help customers compare similar products
   * Highlight key differences between product options
   * Guide customers to the best choice for their specific needs

For product recommendations, always consider the customer's profile information first.
Use tools to check product availability before making recommendations.
Format product information clearly and highlight key benefits relevant to the customer's needs.
"""

# Create product agent with description for automatic delegation
product_agent = Agent(
    model="gemini-2.0-flash",
    name="product_agent",
    global_instruction=GLOBAL_INSTRUCTION,
    instruction=PRODUCT_INSTRUCTION,
    tools=[],
)

async def initialize_product_tools(mcp_tools: List[MCPTool]):
    """Initialize tools for the product agent.

    Args:
        mcp_tools: List of available MCP tools

    Returns:
        The configured product agent
    """
    # Filter for product-related tools
    product_tools = [
        tool
        for tool in mcp_tools
        if tool.name
        in [
            "get-products",
            "get-products-by-collection",
            "get-product-by-id",
            "get-variants-by-ids",
        ]
    ]

    # Add tools to the product agent
    product_agent.tools.extend(product_tools)
    logger.info(f"Added {len(product_tools)} tools to product agent")

    return product_agent
