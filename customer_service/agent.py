# define the MCP tools

import asyncio
import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.agent_tool import AgentTool
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
from typing import Tuple, List
from contextlib import AsyncExitStack
import logging
from google.adk.agents import Agent
from customer_service.prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from customer_service.shared_libraries.callbacks import before_agent
from customer_service.sub_agents import (
    order_agent,
    product_agent,
    initialize_order_tools,
    initialize_product_tools,
)

# Configure logging
logger = logging.getLogger(__name__)

# Global exit stack for resource management
_exit_stack = None
_mcp_tools = None

# Create the agent instance at module level
root_agent = Agent(
    model="gemini-2.0-flash",
    name="shopify_agent",
    global_instruction=GLOBAL_INSTRUCTION,
    sub_agents=[],  # Will be populated during initialization
    instruction=INSTRUCTION,
    before_agent_callback=before_agent,
    tools=[],
)

async def get_shopify_tools() -> Tuple[List[MCPTool], AsyncExitStack]:
    """Get MCP tools from the Shopify server."""
    global _exit_stack, _mcp_tools

    if _mcp_tools is not None:
        return _mcp_tools, _exit_stack

    # Get credentials from environment variables
    shopify_access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
    myshopify_domain = os.environ.get(
        "MYSHOPIFY_DOMAIN", "thesatinstory-in.myshopify.com"
    )

    if not shopify_access_token:
        logger.error("SHOPIFY_ACCESS_TOKEN environment variable not set")
        raise ValueError("SHOPIFY_ACCESS_TOKEN environment variable must be set")

    logger.info("Attempting to connect to Shopify MCP server...")
    try:
        _exit_stack = AsyncExitStack()
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command="node",
                args=[
                    "/Users/tanush/code/d2c-cs-agent/shopify-mcp-server/build/index.js"
                ],
                env={
                    "SHOPIFY_ACCESS_TOKEN": shopify_access_token,
                    "MYSHOPIFY_DOMAIN": myshopify_domain,
                },
            )
        )
        _exit_stack = exit_stack
        _mcp_tools = tools

        logger.info(f"Connected to Shopify MCP server, found {len(tools)} tools")
        return tools, exit_stack
    except Exception as e:
        logger.error(f"Failed to connect to Shopify MCP server: {e}")
        raise


async def initialize_agents_and_tools():
    """Initialize all agents and their tools."""
    global root_agent

    # Get all MCP tools
    tools, exit_stack = await get_shopify_tools()

    # Initialize specialized agents with their tools
    await initialize_order_tools(tools)
    await initialize_product_tools(tools)

    # Add tools to main agent
    root_agent.tools.extend(tools)

    # Add specialized agents to sub_agents list for automatic delegation
    root_agent.sub_agents = [order_agent, product_agent]
    logger.info(
        f"Configured {len(root_agent.sub_agents)} sub-agents for automatic delegation"
    )


async def cleanup():
    """Cleanup MCP resources."""
    global _exit_stack
    if _exit_stack:
        logger.info("Cleaning up Shopify MCP resources")
        await _exit_stack.aclose()
        _exit_stack = None


def register_shutdown_handlers():
    """Register handlers for graceful shutdown."""
    import signal
    import sys

    def signal_handler(sig, frame):
        """Handle termination signals by cleaning up resources."""
        logger.info(f"Received signal {sig}, shutting down...")
        loop = asyncio.get_event_loop()
        loop.create_task(cleanup())
        # Give cleanup a chance to run before exiting
        loop.call_later(1, sys.exit, 0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Registered shutdown handlers")


# Export functions and agent
__all__ = [
    "root_agent",
    "initialize_agents_and_tools",
    "cleanup",
    "register_shutdown_handlers",
]
