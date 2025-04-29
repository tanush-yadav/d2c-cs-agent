"""Customer service module for Kurve."""

from .agent import (
    root_agent,
    initialize_agents_and_tools,
    cleanup,
    register_shutdown_handlers,
)

# Initialize the agent asynchronously
import asyncio

# Try to initialize async resources
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(initialize_agents_and_tools())
    else:
        loop.run_until_complete(initialize_agents_and_tools())
except Exception as e:
    import logging

    logging.getLogger(__name__).error(f"Failed to initialize agents: {e}")

__all__ = ["root_agent", "cleanup", "register_shutdown_handlers"]
