# Best Practices for Agent Architecture (Insights from Travel Concierge)

This document outlines best practices for designing and building multi-agent systems, derived from analyzing the `travel_concierge` agent example.

## Core ADK Agent Types (From Documentation)

Before diving into the specific design patterns, it's helpful to understand the fundamental agent categories provided by Google ADK:

*   **LLM Agents (`LlmAgent`, `Agent`):**
    *   **Engine:** Utilize Large Language Models (LLMs) like Gemini, GPT, Claude.
    *   **Capabilities:** Natural language understanding, reasoning, planning, dynamic tool selection, response generation, delegation to sub-agents.
    *   **Use Case:** Best for flexible, language-centric tasks where understanding context, intent, and generating nuanced responses are key. The primary agent type for conversational AI and complex problem-solving.

*   **Workflow Agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`):**
    *   **Engine:** Deterministic control logic (No LLM for flow control).
    *   **Capabilities:** Manage the execution order and flow of *other* agents in predefined patterns (sequence, parallel, loop).
    *   **Use Case:** Ideal for orchestrating structured processes where the steps are known and predictable. Ensures tasks run in a specific order or concurrently as designed.

*   **Custom Agents:**
    *   **Engine:** Custom Python logic implemented by extending `BaseAgent`.
    *   **Capabilities:** Implement unique operational logic, specialized control flows, or specific integrations not covered by standard types.
    *   **Use Case:** Caters to highly tailored application requirements needing specific, non-standard agent behavior.

Understanding these types helps in selecting the right building blocks for different parts of a multi-agent system.

## 1. Hierarchical Agent Structure

*   **Central Dispatcher:** Employ a root agent (`root_agent` in the example) that acts as a central coordinator. Its primary role is to understand the overall goal or user request, assess the current context (memory, state), and delegate tasks to specialized sub-agents.
*   **Benefit:** Simplifies the root agent's logic by offloading specialized tasks, allowing for focused expertise in sub-agents. Improves modularity.

## 2. Sub-Agent Specialization

*   **Modular Design:** Break down complex tasks (like managing an entire trip) into smaller, manageable sub-tasks or phases, each handled by a dedicated sub-agent (e.g., `inspiration_agent`, `planning_agent`, `booking_agent`, `pre_trip_agent`, `in_trip_agent`, `post_trip_agent`).
*   **Domain/Phase Specificity:** Design sub-agents based on specific domains (e.g., booking flights/hotels) or distinct phases of a process (e.g., pre-trip preparations vs. in-trip assistance).
*   **Benefit:** Enhances maintainability, testability, and allows for independent development and improvement of specific functionalities. Makes it easier to add or modify capabilities without disrupting the entire system.

## 3. Memory and Context-Aware Routing

*   **Leverage Memory/Context:** Utilize memory (like stored user profiles, itineraries) and dynamic context (like the current time) to make informed decisions. In `travel_concierge`:
    *   **Itinerary:** Loaded via `before_agent_callback` from `tools/memory.py`, provides trip dates and details.
    *   **User Profile:** Injected into the prompt (`{user_profile}`), contains user preferences.
    *   **Current Time:** Injected into the prompt (`{_time}`, `{itinerary_datetime}`), crucial for phase determination.
*   **State Determination:** Use context to determine the system's current state. The `root_agent` prompt explicitly defines logic to determine the `Trip phase` (pre\_trip, in\_trip, post\_trip) by comparing the current time to the itinerary's start and end dates.
*   **Dynamic Delegation:** Route requests to the most appropriate sub-agent based on the current state and the nature of the user request.
    *   **Example (Phase-Based):**
        *   *Situation:* Itinerary exists (Dec 10-17), current date is Dec 1st. User asks about required travel documents.
        *   *Context:* `{itinerary_datetime}` < `itinerary_start_date`.
        *   *Action:* `root_agent` determines phase is "pre\_trip" and delegates to `pre_trip_agent`.
        *   *Situation:* Same itinerary, current date is Dec 12th. User asks for restaurant recommendations near their hotel.
        *   *Context:* `itinerary_start_date` <= `{itinerary_datetime}` <= `itinerary_end_date`.
        *   *Action:* `root_agent` determines phase is "in\_trip" and delegates to `in_trip_agent`.
    *   **Example (Request-Based, No Itinerary):**
        *   *Situation:* No itinerary. User asks: "Suggest budget-friendly beach destinations."
        *   *Context:* Request type is exploratory/inspirational.
        *   *Action:* `root_agent` delegates to `inspiration_agent`.
        *   *Situation:* No itinerary. User asks: "Find me flights to Paris for next month."
        *   *Context:* Request type is concrete planning.
        *   *Action:* `root_agent` delegates to `planning_agent`.
*   **Benefit:** Ensures the right agent with the right expertise handles the task based on the actual situation (trip phase, request type), leading to more efficient, relevant, and contextually appropriate responses.

## 4. Clear Prompt Engineering

*   **Define Roles & Responsibilities:** Clearly articulate the purpose, capabilities, limitations, and *specific delegation logic* for each agent (root and sub-agents) in their respective prompts/instructions (see `ROOT_AGENT_INSTR` in `prompt.py`).
*   **Specify Interactions:** Instruct agents on how to interact with users (e.g., tone, brevity), when to use specific tools, and the precise conditions for delegating to other agents.
*   **Context Injection:** Design prompts to effectively utilize dynamically injected context (e.g., `Current user: <user_profile>{user_profile}</user_profile>`, `Current time: {_time}`, `<itinerary>{itinerary}</itinerary>`).
*   **Benefit:** Guides the LLM's behavior effectively, ensuring agents operate within their designated scope, use context correctly, and collaborate as intended.

## 5. Decoupled Tools and External Services (including MCP Implication)

*   **Separate Tool Logic:** Implement tools (functions agents can call, e.g., `places.py`, `search.py`, `memory.py`) in separate modules, distinct from the agent definitions.
*   **Abstract External Calls:** Tools should encapsulate interactions with external APIs or services (e.g., Google Places, Search, databases, flight APIs).
    *   **MCP/Cloud Context:** While this example doesn't explicitly show infrastructure, these external services often run on cloud platforms (GCP, AWS, Azure, etc., sometimes referred to as MCPs). Decoupling means the agent's core logic isn't tied to a specific cloud provider's SDKs. The tool layer handles the interaction.
*   **Well-Defined Interfaces:** Ensure tools have clear inputs and outputs.
*   **Benefit:** Promotes reusability of tools across agents, simplifies tool management/testing, makes the system more resilient to changes in external services, and allows for better management of API keys, monitoring, and potential cloud vendor switching.

## 6. Shared Resources and Libraries

*   **Centralize Common Elements:** Use shared libraries (`shared_libraries/` in the example) for common data structures (e.g., `types.py` defining `Itinerary`, `FlightSegment`), constants (e.g., `constants.py`), or utility functions.
*   **Benefit:** Ensures consistency across the system (agents and tools use the same data formats), reduces code duplication, and makes updates to shared definitions easier.

## 7. State Management / Memory Loading

*   **Callbacks/Hooks:** Utilize mechanisms like `before_agent_callback` (as seen in `agent.py` calling `_load_precreated_itinerary`) to proactively load necessary state or memory (like the user's itinerary) *before* an agent starts processing a user's turn.
*   **Dedicated Memory Tools:** Employ specific tools (`tools/memory.py`) for retrieving and potentially updating persistent information (itineraries, profiles). In a real system, these tools would interact with databases or other persistent storage.
*   **Benefit:** Allows agents to maintain and access relevant context across turns or sessions, enabling stateful conversations and personalized experiences.

## 8. Prompt Structure and Design Insights

Analyzing the `ROOT_AGENT_INSTR` from `travel_concierge/prompt.py` reveals best practices for prompt engineering in agent design:

*   **Define Role and Persona:** Start by clearly stating the agent's role, core purpose, and desired interaction style (e.g., "You are an exclusive travel concierge..."). This grounds the agent's behavior.
*   **Explicit Instructions & Constraints:** Clearly list capabilities, limitations, and rules. Explicitly instruct the agent to use its tools/sub-agents (`- Please use only the agents and tools...`) and follow interaction guidelines (`- ...keep your response limited to a phrase.`).
*   **Structured Delegation Rules:** Provide unambiguous, condition-based rules for routing control to sub-agents. Distinguish between:
    *   *Request-Based Routing:* Triggered by the nature of the user's request (e.g., "If the user asks about inspiration... transfer to `inspiration_agent`").
    *   *State-Based Routing:* Triggered by the system's current state derived from context (e.g., calculating `Trip phase` from time/itinerary and delegating to `pre_trip_agent`, `in_trip_agent`, or `post_trip_agent`).
*   **Clear Context Injection:** Use distinct placeholders (e.g., `{user_profile}`, `{itinerary}`, `{_time}`) for dynamic runtime information. Wrapping context in clear tags (e.g., `<itinerary>...</itinerary>`) can improve LLM parsing. Explicitly tell the agent to *use* the provided context.
*   **Embed State Logic (Optional):** For relatively simple state calculations based directly on injected context (like the `Trip phase` logic), embedding the calculation description within the prompt can be effective.
*   **Formatting for Clarity:** Use markdown (like lists) or other structuring elements to make the prompt easily readable and parsable for the LLM.

## 9. Concluding Best Practices for Agent Design Decisions

Based on the `travel_concierge` analysis, consider these key decision points when designing your agent architecture:

*   **Hierarchy vs. Flat Structure:** For complex tasks with distinct phases or sub-domains, favor a **hierarchical structure** with a root dispatcher and specialized sub-agents over a single monolithic agent. This improves modularity and maintainability.
*   **Specialization Strategy:** Define sub-agents based on **clear functional boundaries** (e.g., handling specific tasks like booking) or **process phases** (e.g., pre-trip, in-trip). Avoid making agents too broad or too granular.
*   **Context Management:** Identify **critical context** needed for decision-making (user data, session state, external data like time). Implement mechanisms (e.g., callbacks, memory tools interacting with databases) to **reliably load and inject** this context into prompts.
*   **Routing Mechanism:** Implement **explicit routing logic** within the dispatcher agent's prompt, clearly defining conditions (based on request type, context, or calculated state) for delegating to each sub-agent.
*   **Prompt Design:** Craft **structured, explicit prompts** for each agent. Define roles, capabilities, constraints, interaction styles, tool usage, context variables, and delegation rules clearly.
*   **Tool Design:** **Decouple tool logic** from agent logic. Encapsulate external API calls or complex computations within tools with well-defined interfaces. This promotes reusability and isolates external dependencies.
*   **Shared Resources:** Centralize common data structures, type definitions, and constants in **shared libraries** to ensure consistency and reduce redundancy across agents and tools.
*   **State Representation:** Decide how to represent and manage state. Simple state logic might live in prompts, while more complex state machines may require dedicated external logic or specific memory tools.

## Summary

The `travel_concierge` agent demonstrates a robust, modular architecture ideal for complex, multi-turn tasks. By employing a hierarchy of specialized agents (`root_agent` dispatching to `inspiration_agent`, `planning_agent`, etc.), leveraging memory (`itinerary`, `user_profile`) and dynamic context (`_time`) for state-aware routing, crafting clear prompts, and decoupling tools/external interactions, it creates a capable, maintainable, and contextually intelligent system. These principles provide a strong foundation for building sophisticated agents.
