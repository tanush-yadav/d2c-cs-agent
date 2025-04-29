/**
 * Order-related tools for the MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import env from '../config/environment.js';
import { ShopifyClient } from '../ShopifyClient/ShopifyClient.js';
import {
  CreateDraftOrderPayload,
} from '../ShopifyClient/ShopifyClientPort.js';
import { handleError } from '../utils/error-handler.js';
import { formatOrder } from '../utils/formatters.js';
import Logger from '../utils/logger.js';

const logger = new Logger('OrderTools');

/**
 * Register order-related tools with the MCP server
 * @param server The MCP server instance
 */
export function registerOrderTools(server: McpServer): void {
  // Get orders
  server.tool(
    'get-orders',
    'Get all orders or filter by criteria',
    {
      limit: z
        .number()
        .optional()
        .default(10)
        .describe('Maximum number of orders to return'),
      orderId: z.string().optional().describe('ID of a specific order to retrieve'),
      customerEmail: z.string().optional().describe('Email of the customer to filter orders by'),
      status: z
        .enum(['any', 'open', 'closed', 'cancelled'])
        .optional()
        .default('any')
        .describe('Status to filter orders by'),
    },
    async (args) => {
      logger.info('Received call: get-orders', { args });
      const { limit, orderId, customerEmail, status } = args;
      const client = new ShopifyClient();
      try {
        if (orderId) {
          const order = await client.loadOrder(
            env.SHOPIFY_ACCESS_TOKEN,
            env.MYSHOPIFY_DOMAIN,
            { id: orderId }
          );
          return {
            content: [{ type: 'text', text: formatOrder(order) }],
          };
        }

        const orders = await client.loadOrders(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          {
            limit,
            status: status !== 'any' ? status : undefined,
            customerEmail,
          }
        );

        if (orders.orders.length === 0) {
          return {
            content: [{ type: 'text', text: 'No orders found matching the criteria.' }],
          };
        }

        const formattedOrders = orders.orders.map(formatOrder);
        return {
          content: [{ type: 'text', text: formattedOrders.join('\n---\n') }],
        };
      } catch (error) {
        return handleError('Failed to retrieve orders', error);
      }
    }
  );

  // Create a draft order
  server.tool(
    'create-draft-order',
    'Create a draft order',
    {
      draftOrderData: z
        .object({
          email: z.string().optional(),
          note: z.string().optional(),
          lineItems: z.array(
            z.object({
              variantId: z.string(),
              quantity: z.number(),
            })
          ),
        })
        .describe('Data for creating a draft order'),
    },
    async (args) => {
      logger.info('Received call: create-draft-order', { args });
      const { draftOrderData } = args;
      const client = new ShopifyClient();
      try {
        const draftOrder = await client.createDraftOrder(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          draftOrderData as CreateDraftOrderPayload
        );
        return {
          content: [
            {
              type: 'text',
              text: `Draft order created successfully. ID: ${draftOrder.draftOrder.id}`,
            },
          ],
        };
      } catch (error) {
        return handleError('Failed to create draft order', error);
      }
    }
  );

  // Complete a draft order
  server.tool(
    'complete-draft-order',
    'Complete a draft order',
    {
      draftOrderId: z.string().describe('ID of the draft order to complete'),
      variantId: z.string().describe('ID of the variant for the draft order'),
    },
    async (args) => {
      logger.info('Received call: complete-draft-order', { args });
      const { draftOrderId, variantId } = args;
      const client = new ShopifyClient();
      try {
        const completedOrder = await client.completeDraftOrder(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          draftOrderId,
          variantId
        );
        return {
          content: [
            {
              type: 'text',
              text: `Draft order completed successfully. Order ID: ${completedOrder.draftOrderComplete.id}`,
            },
          ],
        };
      } catch (error) {
        return handleError('Failed to complete draft order', error);
      }
    }
  );
}