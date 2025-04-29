/**
 * Product-related tools for the MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import env from '../config/environment.js';
import { ShopifyClient } from '../ShopifyClient/ShopifyClient.js';
import { handleError } from '../utils/error-handler.js';
import { formatProduct } from '../utils/formatters.js';
import Logger from '../utils/logger.js';

const logger = new Logger('ProductTools');

/**
 * Register product-related tools with the MCP server
 * @param server The MCP server instance
 */
export function registerProductTools(server: McpServer): void {
  // Get all products or search by title
  server.tool(
    'get-products',
    'Get all products or search by title',
    {
      searchTitle: z
        .string()
        .optional()
        .describe('Search title, if missing, will return all products'),
      limit: z.number().describe('Maximum number of products to return'),
    },
    async (args) => {
      logger.info('Received call: get-products', { args });
      const { searchTitle, limit } = args;
      const client = new ShopifyClient();
      try {
        const products = await client.loadProducts(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          searchTitle ?? null,
          limit
        );
        const formattedProducts = products.products.map(formatProduct);
        return {
          content: [{ type: 'text', text: formattedProducts.join('\n') }],
        };
      } catch (error) {
        return handleError('Failed to retrieve products data', error);
      }
    }
  );

  // Get products from a specific collection
  server.tool(
    'get-products-by-collection',
    'Get products from a specific collection',
    {
      collectionId: z
        .string()
        .describe('ID of the collection to get products from'),
      limit: z
        .number()
        .optional()
        .default(10)
        .describe('Maximum number of products to return'),
    },
    async (args) => {
      logger.info('Received call: get-products-by-collection', { args });
      const { collectionId, limit } = args;
      const client = new ShopifyClient();
      try {
        const products = await client.loadProductsByCollectionId(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          collectionId,
          limit
        );
        const formattedProducts = products.products.map(formatProduct);
        return {
          content: [{ type: 'text', text: formattedProducts.join('\n') }],
        };
      } catch (error) {
        return handleError('Failed to retrieve products from collection', error);
      }
    }
  );

  // Get products by their IDs
  server.tool(
    'get-products-by-ids',
    'Get products by their IDs',
    {
      productIds: z
        .array(z.string())
        .describe('Array of product IDs to retrieve'),
    },
    async (args) => {
      logger.info('Received call: get-products-by-ids', { args });
      const { productIds } = args;
      const client = new ShopifyClient();
      try {
        const products = await client.loadProductsByIds(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          productIds
        );
        const formattedProducts = products.products.map(formatProduct);
        return {
          content: [{ type: 'text', text: formattedProducts.join('\n') }],
        };
      } catch (error) {
        return handleError('Failed to retrieve products by IDs', error);
      }
    }
  );

  // Get variants by their IDs
  server.tool(
    'get-variants-by-ids',
    'Get product variants by their IDs',
    {
      variantIds: z
        .array(z.string())
        .describe('Array of variant IDs to retrieve'),
    },
    async (args) => {
      logger.info('Received call: get-variants-by-ids', { args });
      const { variantIds } = args;
      const client = new ShopifyClient();
      try {
        const response = await client.loadVariantsByIds(
          env.SHOPIFY_ACCESS_TOKEN,
          env.MYSHOPIFY_DOMAIN,
          variantIds
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(response.variants, null, 2),
            },
          ],
        };
      } catch (error) {
        return handleError('Failed to retrieve variants by IDs', error);
      }
    }
  );
}