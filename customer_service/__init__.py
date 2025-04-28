from .agent import root_agent, initialize_shopify_tools, cleanup, register_shutdown_handlers

# Initialize the agent asynchronously
import asyncio

# Try to initialize async resources
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(initialize_shopify_tools())
    else:
        loop.run_until_complete(initialize_shopify_tools())
except Exception as e:
    pass  # Will continue with basic agent functionality

__all__ = ["root_agent", "cleanup", "register_shutdown_handlers"]