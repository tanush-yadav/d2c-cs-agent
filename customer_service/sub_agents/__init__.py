"""Sub-agents package for the customer service agent.

This package contains specialized sub-agents that handle specific aspects
of customer service using ADK's automatic delegation pattern.
"""

# Export sub-agents for easier imports
from .order_agent import order_agent, initialize_order_tools
from .returns_agent import returns_agent, initialize_returns_tools
from .product_agent import product_agent, initialize_product_tools

__all__ = [
    "order_agent",
    "initialize_order_tools",
    "returns_agent",
    "initialize_returns_tools",
    "product_agent",
    "initialize_product_tools",
]
