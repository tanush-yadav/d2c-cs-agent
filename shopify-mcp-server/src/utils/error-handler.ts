/**
 * Centralized error handling for the MCP server
 */
import { ShopifyClientErrorBase } from '../ShopifyClient/ShopifyClientPort.js';
import Logger from './logger.js';

const logger = new Logger('ErrorHandler');

/**
 * Default error response structure
 */
export interface ErrorResponse {
  content: { type: 'text'; text: string }[];
  isError: boolean;
}

/**
 * Handle errors and return consistent error responses
 * @param defaultMessage Default message if error details can't be extracted
 * @param error The error object
 * @returns Formatted error response
 */
export function handleError(defaultMessage: string, error: unknown): ErrorResponse {
  let errorMessage = defaultMessage;
  let errorDetails = '';

  if (error instanceof ShopifyClientErrorBase) {
    errorMessage = error.message;
    if (error.contextData) {
      errorDetails = `\nDetails: ${JSON.stringify(error.contextData)}`;
    }
    // Log the error with its stack trace and context
    logger.error(error.message, {
      errorType: error.constructor.name,
      contextData: error.contextData,
      stack: error.stack,
    });
  } else if (error instanceof Error) {
    errorMessage = error.message;
    // Log the error with its stack trace
    logger.error(error.message, {
      errorType: error.constructor.name,
      stack: error.stack,
    });
  } else {
    // For unknown error types, stringify if possible
    errorDetails = `\nDetails: ${JSON.stringify(error, null, 2)}`;
    logger.error(defaultMessage, { error });
  }

  return {
    content: [{ type: 'text', text: `${errorMessage}${errorDetails}` }],
    isError: true,
  };
}

/**
 * Try to execute a function and handle any errors
 * @param fn Function to execute
 * @param defaultErrorMessage Default error message if the function throws
 * @returns The function result or an error response
 */
export async function tryExecute<T>(
  fn: () => Promise<T>,
  defaultErrorMessage: string
): Promise<T | ErrorResponse> {
  try {
    return await fn();
  } catch (error) {
    return handleError(defaultErrorMessage, error);
  }
}