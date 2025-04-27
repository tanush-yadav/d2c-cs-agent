# D2C Support Bot Scenarios & MCPs

This document outlines realistic Direct-to-Consumer (D2C) support bot scenarios, detailing the customer's request, the bot's internal checks/processes (MCPs - Machine Comprehension Processes), the data sources utilized, and the resulting human-like reply.

## Core Principles & Agent Flow

1.  **Initial Qualification:** The bot first assesses if the query falls within its capabilities based on available MCPs and data sources.
2.  **Information Gathering:** If the query is handleable but lacks necessary details (e.g., order ID, specific product), the bot requests them.
3.  **MCP Execution:** The bot invokes the relevant MCP(s) to retrieve and process information from the appropriate data source.
4.  **Response Framing:** A human-like, helpful response is constructed based on the MCP output.
5.  **Handover Protocol:** If the bot cannot resolve the query (out of scope, requires human intervention), it collects necessary context (customer details, query, product info) and facilitates a real-time handover to a human agent.

## Primary Data Sources / MCPs

The bot primarily relies on two main data sources, each powering specific MCPs:

1.  **Shopify DB MCP Server:** The major data source for transactional and core catalog data.
    *   **Capabilities:** Order lookup, tracking information, customer details, product catalog (basic info, SKUs, inventory), promotions/discounts, return/exchange processing.
2.  **Custom Knowledge Base (KB):** Contains curated documentation, policies, and detailed product information.
    *   **Capabilities:** Product compatibility details, sizing guides, feature explanations, troubleshooting steps, shipping policies (international rules, duties), FAQs, gift recommendations based on curated attributes.

---

## Scenarios Based on Shopify DB MCP Server

These scenarios primarily leverage data and actions handled via the Shopify integration.

### Scenario 1: Order Tracking
[Customer]: When will I get my order?

[Bot] → MCP: Shopify DB Lookup
1.  **Validate:** Extract & verify Order ID from the conversation or customer account.
2.  **Lookup:** Query the Order Management System (via Shopify) for shipping details.
3.  **Fetch:** Call the integrated carrier API (e.g., Shippo, EasyPost via Shopify App/API) for tracking number and current status.
4.  **Estimate:** Pull the expected delivery date from the shipping provider data.
5.  **Frame reply** →

Bot Reply:
Hi Jane—your order #4765 shipped with FastShip yesterday and is currently "In Transit." You can track it here: track.fastship.com/XYZ123. It's due to arrive by April 27. Let me know if you need anything else!

### Scenario 2: Sizing Inquiry (Basic Product Data)
[Customer]: I'm actually a 36C—would this bralette fit me?

[Bot] → MCP: Shopify Product & KB Sizing Guide Lookup
1.  **Check:** Identify which product (by SKU, likely from context or Shopify cart) they're asking about.
2.  **Retrieve:** Pull the linked size chart URL or basic size mapping from Shopify Product data or associated KB entry.
3.  **Clarify:** If chart origin/unit isn't clear (e.g., US/UK/EU) and not specified in data, ask "Is your 36C in US or UK sizing?"
4.  **Recommend:** Map 36C to the brand's recommended size based on the retrieved chart/mapping.
5.  **Frame reply** →

Bot Reply:
Hey there—thanks for asking! Our "Luna" bralette uses US sizing. Based on the chart, a US 36C typically fits our size M. If you're between sizes, the general advice is to size up for extra comfort. Does that help, or would you like a link to the full size-swap guide?

### Scenario 3: Return/Exchange Request
[Customer]: I'd like to return my jacket, please.

[Bot] → MCP: Shopify Order & Returns Process
1.  **Authenticate:** Confirm order belongs to this customer (via Shopify login/lookup) and is within the return window policy (policy details might be in KB, but execution via Shopify).
2.  **Policy Check:** Verify return eligibility via Shopify (item status, tags like 'final sale').
3.  **Generate:** Initiate return process in Shopify or connected Returns app, generating a prepaid label.
4.  **Notify:** Log activity in Shopify customer history/ticketing system and potentially trigger fulfillment team notifications.
5.  **Frame reply** →

Bot Reply:
Absolutely—we've approved your return request for Order #8892 (the jacket). I've initiated the process and emailed you a prepaid return label and instructions. Once our warehouse receives the jacket back in its original condition, you'll see the refund processed to your original payment method within 5–7 business days. Anything else I can do?

### Scenario 4: Coupon Code Not Working
[Customer]: I tried SAVE20 but it says "invalid code."

[Bot] → MCP: Shopify Promotions Lookup
1.  **Verify:** Look up "SAVE20" in the Shopify Promotions/Discounts data (check validity, expiration, usage conditions).
2.  **Check:** Ensure the customer's cart (via Shopify) meets any minimum spend or product eligibility rules for the code.
3.  **Error-map:** Translate the Shopify system error (e.g., expired, min-spend not met, item ineligible) to a user-friendly reason.
4.  **Frame reply** →

Bot Reply:
Oops—it looks like the SAVE20 code expired on April 15th, so it's no longer active. Good news: we currently have a NEW15 code available for 15% off sitewide! This one is valid through May 10th on orders over $50. Would you like me to try applying that to your cart instead?

---

## Scenarios Based on Custom Knowledge Base (KB)

These scenarios primarily rely on information stored in the custom documentation KB.

### Scenario 5: Product Compatibility (Was Scenario 6)
[Customer]: Will this USB-C charger work with my iPhone 12?

[Bot] → MCP: Knowledge Base Lookup (Product Specs)
1.  **Identify:** Identify the specific charger product (e.g., from page context, customer query).
2.  **Retrieve:** Pull the charger's technical specs (output wattage, voltage, protocols like USB-PD) from the KB article for that product.
3.  **Match:** Compare specs against known requirements for iPhone 12 fast-charging (e.g., USB-PD 18W+) stored in a general compatibility section or the iPhone 12 KB page.
4.  **Confirm:** Check the KB for any specific compatibility notes, known issues, or required accessories (like cable type).
5.  **Frame reply** →

Bot Reply:
Yes—the PowerGo USB-C 30W charger (based on its specs in our KB) fully supports USB Power Delivery (USB-PD) and meets Apple's requirements. It will fast-charge your iPhone 12 up to 50% in about 30 minutes. Just be sure to use a USB-C to Lightning cable, as that's not included. Anything else on your mind?

### Scenario 6: Product Recommendation (Was Scenario 15)
[Customer]: I need a gift for a 10-year-old who loves art. Suggestions?

[Bot] → MCP: Knowledge Base Query (Product Catalog - Curated)
1.  **Profile:** (Optional) Check Shopify purchase history for related interests if the customer is logged in.
2.  **Category Query:** Search the KB using tags/keywords like "gift", "art", "kids", "age:10". The KB should have products tagged with relevant attributes.
3.  **Rank:** Sort results based on KB data like "best-seller" flags, review score summaries, or specific "gift recommendation" tags.
4.  **Frame reply** →

Bot Reply:
Great request! Based on our popular art gifts for that age group in the knowledge base, here are a few top suggestions:

*   Acrylic Paint Kit for Kids (Tagged: High-Rated, Age 8+, $29)
*   Deluxe Sketching Set (Tagged: Best-Seller, Age 10+, $34)
*   Color-Changing Watercolors (Tagged: Unique, Age 7+, $22)

Reviews mention these are big hits! I can also add a "GiftWrap" option at checkout via Shopify if you'd like. Which one catches your eye?

### Scenario 7: International Shipping & Duties (Was Scenario 12)
[Customer]: Do you ship to Canada, and who pays duties?

[Bot] → MCP: Knowledge Base Lookup (Policies)
1.  **Zone Check:** Query the KB's Shipping Policy section for Canada's status (enabled/disabled).
2.  **Rate/Duty Lookup:** Retrieve information on how duties are handled for Canada (e.g., DDP - Delivered Duties Paid, DDU - Delivered Duties Unpaid) and associated costs/thresholds from the KB.
3.  **Clarify:** If necessary, explain the DDP vs. DDU implications based on KB definitions.
4.  **Frame reply** →

Bot Reply:
Yes, we do ship to Canada! According to our shipping policy information, we offer Delivered Duties Paid (DDP) shipping at checkout. This means the price you pay includes all duties and taxes, so there are no surprise charges upon delivery. There's a flat $10 fee for shipping & duties on orders under $100. For orders over $100, DDP shipping is complimentary!

---

## Shopify DB MCP Server
## Available tools

This MCP server provides the following tools:

| Tool Name               | Description                                    |
| ----------------------- | ---------------------------------------------- |
| search_dev_docs         | Search shopify.dev documentation               |
| introspect_admin_schema | Access and search Shopify Admin GraphQL schema | -> To be used for DB lookup

## Available prompts

This MCP server provides the following prompts:

| Prompt Name           | Description                                                 |
| --------------------- | ----------------------------------------------------------- |
| shopify_admin_graphql | Help you write GraphQL operations for the Shopify Admin API | -> to be used for creating DB lookup queries

## Development

The server is built using the MCP SDK and communicates with Shopify Dev.

1. `npm install`
1. Modify source files
1. Run `npm run build` to compile
1. Run `npm run test` to run tests
1. Add an MCP server that runs this command: `node <absolute_path_of_project>/dist/index.js`


## Summary Notes (from original)

*   The Knowledge Base often serves as the root source for detailed product understanding, policies, and specialized guidance.
*   The Shopify DB MCP handles core transactional data and processes.
*   The initial qualification and handover logic are crucial for a seamless user experience.

