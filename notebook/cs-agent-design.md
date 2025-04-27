# CX Agent Design based on Travel Concierge Insights & Sample Convos

## 1. Agent Hierarchy

*   **`Root_CX_Agent` (Dispatcher):**
    *   **Role:** Analyzes user queries to understand the core information need. Extracts key entities (Order ID, product identifiers, user details). Determines the primary information source required (Shopify DB, Knowledge Base, or both). Gathers missing context via clarification questions. Routes requests to the appropriate specialized sub-agent (`Shopify_Agent` or `Knowledge_Agent`). Synthesizes final response if needed. Initiates handover if necessary.
    *   **Primary Goal:** Identify the question and determine *which MCP/tool* can provide the answer.

*   **`Shopify_Agent` (MCP / Sub-agent):**
    *   **Role:** Acts as the interface *to the locally running* `shopify-mcp-server` *via the Model Context Protocol (MCP)*. It utilizes the ADK's `MCPToolset` configured for **STDIO transport** to load and expose the specific tools (like `get-products`, `get-orders`, `create-discount`, etc.) defined within the `shopify-mcp-server`. Executes queries and actions based on instructions from the `Root_CX_Agent`.
    *   **Capabilities:** Retrieves order details, tracking info, customer data, basic product attributes (SKU, inventory), promotion status. Processes returns/exchanges via API calls. Creates discounts, manages webhooks, etc., as defined by the exposed MCP tools.
    *   **Tools:** The set of tools provided by the connected `shopify-mcp-server` instance.

*   **`Knowledge_Agent` (MCP / Sub-agent):**
    *   **Role:** Acts as the interface to the Custom Knowledge Base. Retrieves information based on instructions from the `Root_CX_Agent`.
    *   **Capabilities:** Looks up detailed product specifications, compatibility information, sizing guides, company policies (shipping, returns), troubleshooting steps, FAQs, curated recommendation data.
    *   **Tools:** `KB Search Tool`.

*   **`Handover_Logic` (Integrated within `Root_CX_Agent`):**
    *   **Role:** Manages smooth transfer to human agents when the `Root_CX_Agent` determines automated resolution is not possible or optimal.
    *   **Capabilities:** Summarizes conversation context, identifies reason for handover, triggers the handover process.
    *   **Tools:** `Handover Initiation Tool`.

## 2. Memory Handling

*   **Session Memory (Framework):** Stores conversation history, extracted entities (Order ID, Product SKU, User Size/Preferences, Customer Info if logged in). Managed by the agent platform (ADK). Essential for multi-turn context.
*   **Persistent Memory (External Data Sources):**
    *   **Shopify DB:** The primary source for transactional, customer, and core product data. Accessed *exclusively* via the `Shopify_Agent`.
    *   **Custom Knowledge Base (KB):** The primary source for detailed product understanding, policies, curated content, and FAQs. Accessed *exclusively* via the `Knowledge_Agent`.
*   **Loading/Access:** The `Root_CX_Agent` identifies necessary context (e.g., Order ID, product SKU). This context is passed to the designated sub-agent (`Shopify_Agent` or `Knowledge_Agent`), which then uses its tool to query the relevant external data source.

## 3. State Handling (Information Flow)**

State represents the agent's current step in the information retrieval and response generation process, rather than fixed task types.

*   **Core States:**
    *   `STATE_ANALYZING_INTENT`: `Root_CX_Agent` processing the incoming user query.
    *   `STATE_GATHERING_CONTEXT`: `Root_CX_Agent` asking clarifying questions (e.g., "What is your order number?", "Which specific product are you asking about?").
    *   `STATE_ROUTING_TO_SHOPIFY`: `Root_CX_Agent` determined Shopify data is needed; preparing to delegate.
    *   `STATE_QUERYING_SHOPIFY`: `Shopify_Agent` is actively using its tool to interact with the Shopify DB.
    *   `STATE_ROUTING_TO_KB`: `Root_CX_Agent` determined KB information is needed; preparing to delegate.
    *   `STATE_QUERYING_KB`: `Knowledge_Agent` is actively using its tool to search the KB.
    *   `STATE_SYNTHESIZING_RESPONSE`: An agent (usually Root, but could be sub-agent for simple lookups) is formulating the answer based on retrieved data.
    *   `STATE_HANDOVER_REQUIRED`: `Root_CX_Agent` determined automated resolution failed or is inappropriate.

*   **Example Flow (Sizing Question):**
    1.  *User:* "Will this Luna bralette fit me? I'm a 36C."
    2.  `Root_CX_Agent`: `STATE_ANALYZING_INTENT`. -> Identifies need for product specs/sizing chart (KB) and potentially product confirmation (Shopify if ambiguous). Extracts "Luna bralette", "36C".
    3.  `Root_CX_Agent`: Determines KB is primary source. -> `STATE_ROUTING_TO_KB`.
    4.  `Root_CX_Agent` delegates task ("Find size info for Luna bralette and check fit for 36C") to `Knowledge_Agent`.
    5.  `Knowledge_Agent`: `STATE_QUERYING_KB`. -> Uses `KB Search Tool` ("Luna bralette size chart"). Retrieves chart data.
    6.  `Knowledge_Agent`: `STATE_SYNTHESIZING_RESPONSE`. -> Compares "36C" to chart. Finds match (e.g., "M"). Formulates response.
    7.  `Knowledge_Agent` returns result ("Size M recommended based on chart.") to `Root_CX_Agent`.
    8.  `Root_CX_Agent`: `STATE_SYNTHESIZING_RESPONSE`. -> Adds conversational context/niceties. Sends final reply to user.

## 4. Tools (Summary)

*   **`Shopify DB Tool`:** *This isn't a single tool but represents the collection of tools exposed by the locally running `shopify-mcp-server` via MCP (using **STDIO** transport, typically interacting with `node build/index.js`). The `Shopify_Agent` uses the ADK's `MCPToolset` (configured appropriately for STDIO, *not* the SSE example provided elsewhere) to connect to this server process and make these specific tools available (e.g., `get-products`, `get-orders`, `create-discount`, `manage-webhook`, etc.). Direct interaction for testing/debugging this MCP server is often done via the MCP Inspector tool (e.g., `http://127.0.0.1:6274`).*
*   **`KB Search Tool`:** Interface for `Knowledge_Agent` (e.g., vector search, keyword search).
*   **`Handover Initiation Tool`:** Interface for `Root_CX_Agent`'s handover logic.

## 5. Future Development Plan (Detailed)

Based on the initial design, the following areas require further development to create a fully functional agent:

*   **Knowledge Agent Tooling:** - No need to implement right now.
    *   **Implement `KB Search Tool`:**
        *   Create a Python class `KBSearchTool` inheriting from `adk.tools.Tool`.
        *   Define input schema (e.g., `query: str`, `filters: Optional[dict]`) and output schema (e.g., `results: List[dict]`, where each dict contains `content`, `source`, `score`).
        *   **Initial Backend Integration (V1):** Start with a simple backend, like searching through Markdown files in a specific directory or using a basic keyword search on a JSON/CSV file.
        *   **Advanced Backend Integration (V2+):** Integrate with a vector database (e.g., Pinecone, ChromaDB, Weaviate) for semantic search. This requires:
            *   Setting up the vector DB instance.
            *   Developing a data ingestion pipeline: Script to chunk documents (product descriptions, policies, FAQs), generate embeddings (using e.g., Sentence Transformers or an API like OpenAI), and store them in the vector DB.
            *   Implementing the search logic within the `KBSearchTool` to query the vector DB based on the user's query embedding.
    *   **Data Curation:** Establish a process for adding, updating, and maintaining the information in the knowledge base backend.

*   **User Context Loading:**
    *   **Mechanism:** Inject user context (Customer ID, name, email, potentially past order IDs or preferences if available) during the initialization of the `Root_CX_Agent`. This could be done by passing a `user_context` dictionary or object to the agent's `run` or `stream` method.
    *   **ADK Integration:** Utilize ADK's context variables or modify the agent's initialization to accept and store this context.
    *   **Prompt Modification:** Update the `Root_CX_Agent`'s system prompt to include placeholders for user context, e.g., "You are assisting customer {customer_name} (ID: {customer_id}). Their recent order IDs are {recent_order_ids}." The agent should be instructed on how to use this information appropriately (e.g., "Do not ask for information already present in the context unless confirmation is needed.").
    *   **PII Handling:** Ensure compliance with data privacy regulations. Avoid logging sensitive user data unnecessarily and be mindful of how PII is used in prompts and stored in memory.

*   **Memory Management:**
    *   **Initial Approach:** Rely on the default ADK session memory (e.g., `ConversationBufferMemory`) which stores the conversation history. This is suitable for maintaining context within a single session.
    *   **Entity Extraction & Storage:** Enhance the `Root_CX_Agent`'s prompt or add a dedicated processing step to explicitly extract key entities (Order ID, Product SKU, user preferences like size/color) mentioned during the conversation. Store these extracted entities within the ADK's memory (perhaps in a dedicated field or using a more structured memory type like `ConversationEntityMemory` if available/implemented).
    *   **Long-Term Memory (Optional):** For persisting user preferences or summaries across sessions, evaluate if integration with an external user profile store is needed. This is likely out of scope for the initial versions.

*   **Error Handling:**
    *   **Tool Errors:** Implement `try...except` blocks around tool execution calls within the agents (`Shopify_Agent`, `Knowledge_Agent`). Catch specific exceptions (e.g., `MCPToolError`, `KBConnectionError`).
    *   **Agent Logic Errors:** Handle potential failures in state transitions or response synthesis.
    *   **Error Reporting:** Log errors comprehensively (e.g., timestamp, agent state, error message, traceback).
    *   **User Feedback:** Provide user-friendly error messages (e.g., "I encountered an issue trying to retrieve that information. Could you please try rephrasing?", "I'm having trouble connecting to the order system right now.").
    *   **Retry Mechanisms:** Implement simple retry logic for transient errors (e.g., network timeouts when calling MCP tools).
    *   **Handover Trigger:** Use persistent errors or specific error types (e.g., authentication failure with Shopify) as potential triggers for the `Handover_Logic`.

*   **Handover Implementation:**
    *   **`Handover Initiation Tool`:**
        *   Create a Python class `HandoverTool` inheriting from `adk.tools.Tool`.
        *   Define input schema (e.g., `reason: str`, `summary: str`, `user_id: str`).
        *   Implement the tool's execution logic: This could involve calling an external API (e.g., Zendesk, Intercom), sending a message to a Slack channel, or queuing the request in a dedicated system, passing the conversation summary and reason.
    *   **Handover Logic in `Root_CX_Agent`:**
        *   Refine the prompt and internal logic to identify handover scenarios:
            *   Explicit user request ("talk to a human").
            *   Sentiment analysis indicating high user frustration.
            *   Repeated failure to resolve the query after N turns (e.g., 2-3 attempts).
            *   Detection of complex issues outside the agent's defined capabilities.
            *   Specific error conditions (see Error Handling).
        *   Instruct the agent to generate a concise summary of the conversation and the reason for handover before calling the `HandoverTool`.

*   **Testing and Refinement:**
    *   **Unit Tests:** Test individual tools (`KBSearchTool`, `HandoverTool`) with mock inputs and backends. Test MCP tool interactions if possible.
    *   **Integration Tests:** Test the interaction between agents (Root delegating to Shopify/Knowledge) for specific query types.
    *   **End-to-End (E2E) Tests:** Create a suite of representative customer conversation scripts (e.g., order status check, sizing question, return request, complex multi-part query, handover scenario). Run these scripts against the full agent system.
    *   **Evaluation Metrics:** Track key metrics during testing:
        *   Task Success Rate (did the agent fulfill the user's request?).
        *   Turn Count (efficiency).
        *   Handover Rate (and reasons for handover).
        *   Tool Call Success/Failure Rates.
        *   User Satisfaction (if simulated or gathered via feedback).
    *   **Iterative Refinement:** Use test results, logs, and failed conversations to:
        *   Improve agent prompts (clarity, instruction tuning).
        *   Refine routing logic in `Root_CX_Agent`.
        *   Adjust tool descriptions or functionalities.
        *   Enhance KB content based on information gaps.
