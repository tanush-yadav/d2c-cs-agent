/**
 * Tool registry for the MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import Logger from '../utils/logger.js';
import { registerOrderTools } from './order-tools.js';
import { registerProductTools } from './product-tools.js';

const logger = new Logger('ToolRegistry');

/**
 * Register all tools with the MCP server
 * @param server The MCP server instance
 */
export function registerAllTools(server: McpServer): void {
  logger.info('Registering all tools with the MCP server');

  // Register product tools
  registerProductTools(server);

  // Register order tools
  registerOrderTools(server);

  // Additional tool categories can be registered here

  logger.info('All tools registered successfully');
}