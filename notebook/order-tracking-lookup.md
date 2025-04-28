# Order Lookup and Tracking Implementation Plan (Revised)

## Level 1: Goal

Implement a reliable and user-friendly "Where's my order?" flow within the `@customer_service` agent, allowing users to easily check order status and tracking, confirm implicit orders, and handle common follow-up requests regarding delivery timing.

## Level 2: Strategy

1.  **Tool Definition:** Define clear interfaces for tools that fetch order details (`get_order`), track shipments (`track_package`), find recent user orders (`get_recent_orders`), and handle policy-based requests (`handle_delivery_request`).
2.  **Conditional Agent Logic:** Enhance the agent's core logic and prompts to:
    *   Recognize "Where's my order?" intent.
    *   Check for a provided order ID.
    *   If no ID, use `get_recent_orders` to check for a single recent order.
    *   Prompt user for confirmation if a single recent order is found.
    *   Request the order ID if multiple or no recent orders exist.
    *   Once an order ID is confirmed/provided, use `get_order` and `track_package`.
    *   Synthesize a user-friendly status response.
    *   Recognize follow-up requests about expediting or delaying delivery.
    *   Route delivery timing requests to `handle_delivery_request`.
3.  **Phased Implementation (MCP Focus):** Define ADK tools initially. Implement backend logic within an external MCP server (`@shopify-mcp-server`) accessed via `StdioServer`, starting with mocks where necessary (`handle_delivery_request`).
4.  **Robust Testing:** Implement comprehensive tests covering the standard flow, the conditional single-order confirmation logic, error handling, and the routing to the policy tool. Aim for 100% coverage for this extended path.

## Level 3: Tactics

1.  **Create/Update ADK Tool Definitions (`customer_service/tools/order_tools.py`):**
    *   `get_order(order_id)`: Docstring describes fetching order details (items, address, **tracking number**). Relies on MCP server.
    *   `track_package(tracking_number)`: Docstring describes fetching shipment status/history. Relies on MCP server.
    *   `get_recent_orders()`: Docstring describes fetching a list of recent orders for the *current user* (implies user context is available). Returns a list of basic order info (ID, date, items summary). Relies on MCP server. Initially mockable within ADK if needed before MCP implementation.
    *   `handle_delivery_request(order_id: str, request_type: Literal['expedite', 'delay'], reason: str | None = None)`: Docstring describes checking policy and attempting to modify delivery schedule. `request_type` specifies user intent. Returns success/failure/policy info. **Initially implement as a mock ADK tool.**
2.  **MCP Server Implementation (`@shopify-mcp-server`):**
    *   Implement `get_order`, `track_package`, and `get_recent_orders` logic using Shopify API.
    *   Ensure server exposes these via MCP over stdio.
3.  **Update Prompts (`customer_service/prompts.py`):**
    *   Refine `GLOBAL_INSTRUCTION` / `INSTRUCTION` to guide the agent through the conditional logic:
        *   If intent is order status and `order_id` is missing:
            *   Call `get_recent_orders`.
            *   If result is one order: Ask user "Are you asking about order #{order_id} placed on {date} containing {item_summary}?"
            *   If result is multiple/zero: Ask "Could you please provide the order ID you're asking about?"
        *   If intent is order status and `order_id` is present/confirmed:
            *   Call `get_order` with `order_id`.
            *   If successful and `tracking_number` exists: Call `track_package` with `tracking_number`.
            *   Format a reply combining order status and tracking info (e.g., "Your order #{order_id} shipped on {date} and is currently {tracking_status}. You can track it here: {tracking_link}"). Handle cases where tracking isn't available yet.
        *   If user asks to expedite or delay after getting status:
            *   Extract `order_id`, intent (`expedite`/`delay`), and any user-provided `reason`.
            *   Call `handle_delivery_request`.
            *   Relay the result (e.g., "I've put in a request to expedite order #{order_id}. According to policy, we can/cannot guarantee earlier delivery...", or "Okay, I've submitted a request to delay order #{order_id}...").
4.  **Register Tools & Configure MCP:**
    *   Import all four tool definitions (`get_order`, `track_package`, `get_recent_orders`, `handle_delivery_request`) into `customer_service/agent.py`.
    *   Add them to the `tools` list for the agent.
    *   Configure the ADK runtime to connect `get_order`, `track_package`, and `get_recent_orders` to the `@shopify-mcp-server` via `StdioServer`. `handle_delivery_request` will run directly as a Python function (mock initially).
5.  **Testing:**
    *   **MCP Server Unit Tests:** Test Shopify logic for the three MCP tools.
    *   **ADK Tool Unit Tests:** Test the mock `handle_delivery_request`.
    *   **Integration Tests:** Test ADK agent <-> MCP server connection. Test the agent's ability to follow the conditional logic (no ID -> recent orders -> confirm/ask). Test routing to `handle_delivery_request`.
    *   **End-to-End Tests:** Test the full flow via chat UI against Shopify sandbox, covering: providing ID, not providing ID (single recent, multi/no recent), successful tracking, no tracking yet, asking to expedite, asking to delay.

## Level 4: Execution Plan (Initial - Mocks/Definitions)

1.  **Why?** Define all tool interfaces and implement the core conditional logic in the agent's prompts, using mocks for external dependencies and new policy functions. Allows rapid iteration on the agent's conversation flow.
2.  **How?**
    *   Create/update `customer_service/tools/order_tools.py`:
        *   Define `get_order`, `track_package`, `get_recent_orders` with docstrings only (targeting MCP).
        *   Define and implement *mock* `handle_delivery_request` function (e.g., always returns a canned policy response).
    *   Implement mock logic for `get_recent_orders` *temporarily within the agent or a simple mock function* if needed for prompt testing before MCP server is ready (e.g., always return one order, or zero orders, to test different branches).
    *   Import and register all four tools in `customer_service/agent.py`.
    *   Refine prompts in `customer_service/prompts.py` to implement the full conditional logic described in Level 3.
    *   Run initial tests focusing on the agent's decision-making and conversational flow for all branches.

## Level 5: Execution Plan (Integration & Testing)

1.  **Why?** Connect the agent to the live MCP server for real data and test the complete, integrated system for reliability and accuracy.
2.  **How?**
    *   Finalize and deploy the `@shopify-mcp-server` with `get_order`, `track_package`, and `get_recent_orders` capabilities via stdio MCP.
    *   Configure the ADK runtime environment to launch and connect to the `@shopify-mcp-server`. Remove any temporary mocks for `get_recent_orders` if used in Level 4.
    *   Implement comprehensive tests:
        *   Verify MCP server functions correctly against Shopify sandbox.
        *   Verify ADK agent <-> MCP communication.
        *   Verify the agent correctly handles the single-order confirmation flow with real data.
        *   Verify the agent correctly calls `handle_delivery_request` for follow-up questions.
        *   Perform end-to-end smoke tests covering all scenarios described in Level 3 Testing.
    *   (Future) Decide whether `handle_delivery_request` should remain an ADK mock, become a full ADK tool with real logic, or be moved into the MCP server.
    *   Verify 100% test coverage for the entire revised order lookup/tracking and delivery request flow.
