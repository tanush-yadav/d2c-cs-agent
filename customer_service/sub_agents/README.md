# Agent Architecture

This directory contains specialized sub-agents that handle specific customer service functions using ADK's automatic delegation pattern.

## Agent Delegation Model

The customer service system uses a multi-agent architecture with automatic delegation:

```
┌────────────────────┐
│                    │
│   Main Agent       │◄────► Customer
│   (shopify_agent)  │      Interaction
│                    │
└─────────┬──────────┘
          │
          │ Delegates based on query type
          ▼
┌─────────┴──────────┬─────────────────────┬────────────────────┐
│                    │                     │                    │
│   Order Agent      │   Returns Agent     │   Product Agent    │
│                    │                     │                    │
└────────────────────┴─────────────────────┴────────────────────┘
```

## Agents Overview

### Main Agent (shopify_agent)
- Entry point for all customer interactions
- Handles general inquiries and cart management
- Delegates specialized inquiries to appropriate sub-agents
- Configuration in `customer_service/agent.py`

### Order Agent (order_agent.py)
- Specializes in order tracking, history, and status inquiries
- Handles the complex case of matching order numbers to internal IDs
- Uses both `get_orders` and `get_order` tools to provide accurate information

### Returns Agent (returns_agent.py)
- Handles returns, exchanges, refund policies, and procedures
- Guides customers through return processes
- Provides policy information and status updates

### Product Agent (product_agent.py)
- Provides expert product recommendations
- Handles detailed product inquiries and comparisons
- Uses product recommendation tools to suggest appropriate products

## Delegation Logic

Delegation occurs automatically through ADK's sub-agent pattern. The main agent evaluates the customer's query and its context, and automatically transfers control to the appropriate specialized agent based on:

1. The query content (keywords like "order", "return", "product")
2. The sub-agent descriptions
3. The delegation instructions in the main agent's prompt

After the specialized agent handles the query, control returns to the main agent for subsequent interactions.

## Adding New Sub-Agents

To add a new specialized agent:

1. Create a new file in the `sub_agents` directory
2. Define the agent with a clear `description` parameter for delegation
3. Implement initialization function to give it appropriate tools
4. Update `agent.py` to include the new agent in the `sub_agents` list
5. Update `prompts.py` to include delegation instructions for the new agent