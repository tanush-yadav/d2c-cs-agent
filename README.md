# Kurve D2C Shapewear Customer Service Agent

This project implements an AI-powered customer service agent for Kurve, a direct-to-consumer (D2C) brand specializing in affordable women's shapewear. The agent is designed to provide expert product assistance, including recommendations, fit guidance, and feature explanations, leveraging integration with Shopify.

## Overview

The Kurve Customer Service Agent aims to provide a seamless and personalized shopping experience. It leverages Gemini to understand customer needs, offer tailored product recommendations based on preferences and body type, provide detailed product information including sizing, and answer common questions about Kurve's shapewear products. The agent interacts with a Shopify store via a dedicated MCP (Model Context Protocol) server.

## Agent Details

The key features of the Customer Service Agent include:

| Feature            | Description                 |
| ------------------ | --------------------------- |
| _Interaction Type_ | Conversational              |
| _Complexity_       | Intermediate                |
| _Agent Type_       | Single Agent (with sub-agents potentially) |
| _Components_       | Tools, Live (via MCP)       |
| _Vertical_         | Retail (D2C E-commerce)     |

### Agent Architecture

The agent utilizes the Google Agent Development Kit (ADK) and communicates with a Shopify store through a Node.js/TypeScript MCP server (`shopify-mcp-server`). This server handles the actual Shopify Admin API GraphQL requests. The agent's core logic resides in Python (`customer_service` directory), managing conversation flow and tool usage.

Specific components include:
- **Main Agent Logic:** [customer_service/agent.py](mdc:customer_service/agent.py)
- **Configuration:** [customer_service/config.py](mdc:customer_service/config.py)
- **Prompts:** [customer_service/prompts.py](mdc:customer_service/prompts.py)
- **Sub-Agents (e.g., Product):** [customer_service/sub_agents/](mdc:customer_service/sub_agents/)
- **Agent Tools (Python Wrappers):** [customer_service/tools/](mdc:customer_service/tools/)
- **Shopify MCP Server:** [shopify-mcp-server/](mdc:shopify-mcp-server/)

*(Note: The architecture diagram reference from the previous README has been removed as it depicted a different agent.)*

This agent connects to a live Shopify backend via the MCP server. Changes made through tools (if implemented, e.g., adding to cart) should reflect in the actual Shopify store, assuming the MCP server tools have write capabilities and necessary permissions.

### Key Features

- **Personalized Customer Assistance:**
  - Can be extended to greet returning customers and reference purchase history (requires customer identification/CRM integration).
  - Maintains a helpful and knowledgeable tone specific to the Kurve brand.
- **Product Identification and Recommendation:**
  - Assists customers in finding products based on needs (e.g., occasion, desired compression, style).
  - Recommends specific shapewear items based on customer preferences, body type, and stated needs.
  - Suggests complementary products or alternatives.
- **Product Information & Fit Guidance:**
  - Provides detailed information about product features, materials, benefits, and care.
  - Answers sizing questions using size chart data retrieved from Shopify variant metafields.
  - Helps customers compare similar products.
- **Shopify Integration:**
  - Uses tools that interact with the Shopify MCP server to query product and variant data.
  - Can be extended to handle cart modifications, order lookups, and other Shopify actions.
- **Tool-Based Interactions:**
  - The agent interacts with the user using a set of tools mapped to Shopify MCP server endpoints.
  - The agent can use multiple tools in a single interaction.
  - Tools retrieve live data from Shopify (e.g., product details, variant pricing, size charts).
- **Evaluation:**
  - The agent can be evaluated using a set of test cases targeting its ability to use tools correctly and respond accurately based on retrieved Shopify data.

#### Agent State - Default customer information

The agent's session state can be preloaded with sample customer data for simulation. In a production scenario, this state should ideally be loaded from a CRM or customer database at the start of the conversation. This assumes user authentication.

#### Tools (via Shopify MCP Server)

The agent primarily uses tools that interact with the `shopify-mcp-server`. Key examples include:

- `get-products`: Retrieves a list of products, optionally filtered by title.
- `get-products-by-collection`: Retrieves products belonging to a specific collection.
- `get-product-by-id`: Fetches detailed information for a single product ID (Not currently implemented in MCP server).
- `get-products-by-ids`: Fetches detailed information for multiple product IDs.
- `get-variants-by-ids`: Fetches detailed information for specific product variant IDs, including price, SKU, and potentially size chart metafields.
- *(Other potential tools: `get-orders`, `get-customer`, `create-discount`, `manage-cart` etc. - depending on implementation in the MCP server and agent)*

*(Note: The list above replaces the Cymbal-specific tools. The actual available tools depend on the implementation in `shopify-mcp-server/src/index.ts` and their registration in `customer_service/agent.py` or relevant sub-agents like `customer_service/sub_agents/product_agent.py`.)*

## Setup and Installations

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Node.js and npm (for the Shopify MCP Server)
- Google ADK SDK (installed via Poetry)
- Google Cloud Project (for Vertex AI Gemini integration)
- Shopify Development Store or access to a Shopify Store Admin API
  - Access Token (`SHOPIFY_ACCESS_TOKEN`) with necessary permissions (e.g., `read_products`, `read_variants`).
  - Store Domain (`MYSHOPIFY_DOMAIN`).

### Installation
1.  **Google Cloud Prerequisites:**

    If deploying via Agent Engine or using Vertex AI, ensure your Google Cloud project is set up:
    ```bash
    gcloud auth login
    gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
    ```

2.  Clone the repository (assuming it contains both `customer_service` and `shopify-mcp-server`):

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

3.  **Install Python Agent Dependencies:**
    Navigate to the Python agent directory and install dependencies:
    ```bash
    cd customer_service
    poetry install
    # Activate the virtual environment
    poetry shell
    cd ..
    ```

4.  **Install Shopify MCP Server Dependencies:**
    Navigate to the MCP server directory and install dependencies:
    ```bash
    cd shopify-mcp-server
    npm install
    cd ..
    ```

5.  **Set up Environment Variables:**
    Create a `.env` file in the root directory (or configure environment variables directly). Minimally, you'll need Shopify credentials:
    ```dotenv
    # Shopify Credentials (for shopify-mcp-server)
    SHOPIFY_ACCESS_TOKEN=YOUR_SHOPIFY_ADMIN_API_ACCESS_TOKEN
    MYSHOPIFY_DOMAIN=your-store-name.myshopify.com

    # Google Cloud Credentials (if using Vertex AI)
    GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_LOCATION=us-central1
    ```
    The Shopify MCP server (`shopify-mcp-server/src/index.ts`) reads these environment variables. Ensure the Python agent configuration (`customer_service/config.py`) is also set up if needed.

## Running the Agent

The agent requires **two** components to be running: the Python agent logic and the Node.js Shopify MCP server.

1.  **Run the Shopify MCP Server:**
    Open a terminal, navigate to the `shopify-mcp-server` directory, build the TypeScript code, and run the server:
    ```bash
    cd shopify-mcp-server
    npm run build
    npm start
    # Keep this terminal running
    ```
    *(Ensure your .env file with Shopify credentials is in the root directory or the variables are otherwise accessible to the Node.js process)*

2.  **Run the Python Agent:**
    Open a *separate* terminal, ensure you are in the Python agent's virtual environment (`poetry shell`), and run the agent using ADK:
    ```bash
    # Make sure you are in the root directory containing customer_service
    adk run customer_service --mcp shopify-tools=./shopify-mcp-server/build/index.js
    ```
    Or run via the ADK Web UI:
    ```bash
    # Make sure you are in the root directory containing customer_service
    adk web --mcp shopify-tools=./shopify-mcp-server/build/index.js
    ```
    Select `customer_service` from the dropdown in the Web UI. The `--mcp` flag tells the ADK how to launch the Shopify tool server.

### Example Interaction

Here's an example of how a user might interact with the Kurve agent:

**User:**
Hi, I'm looking for a bodysuit for under a tight dress. What do you recommend?

**Agent:**
Hi there! For a smooth silhouette under a tight dress, our ShapeShifter Bodysuit is very popular. It offers firm compression and comes in both strapless and strapped versions. Do you know what size you might need?

**User:**
I think I'm a Medium, but I want to be sure. My chest is 38 inches.

**Agent:**
Okay, let me check the sizing for the ShapeShifter Bodysuit in Medium.
```tool_code
print(get_products(searchTitle='ShapeShifter Bodysuit', limit=1))
```
```tool_outputs
  Product: ShapeShifter Bodysuit
  description: Forget the hassle of wearing... JUMP ON THE KURVE REVOLUTION!
  handle: shapewear-bodysuit
  variants: variant.title: Strapless (Detachable straps) / Black / S, variant.id: gid://shopify/ProductVariant/44169145942230, variant.price: 1310.00, variant.sku: , variant.inventoryPolicy: CONTINUE, variant.sizeChart: {
  "bust_inches": "32-34",
  "waist_inches": "25-27"
}, variant.title: Strapless (Detachable straps) / Black / M, variant.id: gid://shopify/ProductVariant/44169145974998, variant.price: 1310.00, variant.sku: , variant.inventoryPolicy: CONTINUE, variant.sizeChart: {
  "bust_inches": "35-38",
  "waist_inches": "28-31"
}, ... (other variants) ...
```
**Agent:**
Thanks! Based on the size chart for the Medium variant, it fits chest measurements of 35-38 inches. Since you're right at 38 inches, the Medium should provide a snug, compressive fit. If you prefer slightly less compression, the Large fits 39-42 inches. Would you like to add the Medium to your cart, or perhaps see the Large?

## Evaluating the Agent

Evaluation tests assess the overall performance and capabilities of the agent.

**Steps:**

1.  **Run Evaluation Tests:**
    Ensure you are in the `customer_service` directory with the Poetry environment activated.
    ```bash
    pytest eval
    ```
    - This command executes all test files within the `eval` directory. Evaluation might need adjustments based on the live Shopify integration.

## Unit Tests

Unit tests focus on testing individual units or components of the code in isolation.

**Steps:**

1.  **Run Agent Unit Tests:**
    Ensure you are in the `customer_service` directory with the Poetry environment activated.
    ```bash
    pytest tests/unit
    ```
    - This command executes all test files within the `tests/unit` directory.

2.  **Run MCP Server Unit Tests (if applicable):**
    Navigate to the `shopify-mcp-server` directory. If tests are configured (e.g., in `package.json`), run them:
    ```bash
    cd ../shopify-mcp-server
    npm test # Or the specific command configured for tests
    cd ..
    ```

## Configuration

- **Agent Configuration:** Found in [customer_service/config.py](mdc:customer_service/config.py). Includes parameters like agent name, app name, and LLM model.
- **Shopify MCP Server:** Configuration relies on environment variables (`SHOPIFY_ACCESS_TOKEN`, `MYSHOPIFY_DOMAIN`). API version and other settings are in [shopify-mcp-server/src/ShopifyClient/ShopifyClient.ts](mdc:shopify-mcp-server/src/ShopifyClient/ShopifyClient.ts).

## Deployment on Google Agent Engine

Deploying requires building both the Python agent and potentially packaging the MCP server if it needs to run alongside the agent in the deployed environment.

1.  **Build Customer Service Agent WHL file**
    Navigate to the `customer_service` directory:
    ```bash
    cd customer_service
    poetry build --format=wheel --output=../deployment # Build into a deployment folder at the root
    cd ..
    ```

2.  **(Optional) Prepare MCP Server for Deployment:**
    Depending on the deployment strategy, you might need to bundle the `shopify-mcp-server` or ensure it runs separately and is accessible by the deployed agent. The standard `deploy.py` might not handle the Node.js server automatically.

3.  **Deploy the agent to Agent Engine:**
    Review and potentially adapt the standard `deploy.py` script (likely placed in the `deployment` folder) to handle the specifics of this agent and its MCP dependency.
    ```bash
    cd deployment
    # Ensure deploy.py is present and configured
    python deploy.py
    ```

### Testing deployment

This code snippet is an example of how to test the deployed agent. You will need the deployed agent's resource name.

```python
import vertexai
from customer_service.config import Config # Assuming config is available or adapt path
from vertexai.preview.reasoning_engines import ReasoningEngine # Updated import

# configs = Config() # May not be needed if config is packaged

vertexai.init(
    project="<YOUR_GOOGLE_CLOUD_PROJECT_ID>", # Use your actual Project ID
    location="<YOUR_GOOGLE_CLOUD_LOCATION>"  # Use the region where deployed
)

# Get the agent based on resource name (replace with your actual resource name)
# Example: projects/your-project-id/locations/us-central1/reasoningEngines/your-engine-id
agent_engine = ReasoningEngine("DEPLOYMENT_RESOURCE_NAME")

# Example query (replace USER_ID and session_id if needed)
response = agent_engine.query(
    input="Hi, tell me about your bodysuits."
    # user_id=USER_ID, # If required by your agent/setup
    # session_id=session["id"], # If managing sessions explicitly
)

print(response)

# If using streaming:
# for chunk in agent_engine.stream_query(...):
#    print(chunk)

```
