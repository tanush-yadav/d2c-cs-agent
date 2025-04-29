/**
 * Environment configuration with validation
 */
import { z } from 'zod';

const environmentSchema = z.object({
  SHOPIFY_ACCESS_TOKEN: z.string({
    required_error: 'SHOPIFY_ACCESS_TOKEN environment variable is required',
  }),
  MYSHOPIFY_DOMAIN: z.string({
    required_error: 'MYSHOPIFY_DOMAIN environment variable is required',
  }),
  SHOPIFY_API_VERSION: z.string().default('2024-04'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export type Environment = z.infer<typeof environmentSchema>;

/**
 * Loads and validates environment variables
 * @returns Validated environment variables
 * @throws Error if required environment variables are missing
 */
export function loadEnvironment(): Environment {
  try {
    return environmentSchema.parse({
      SHOPIFY_ACCESS_TOKEN: process.env.SHOPIFY_ACCESS_TOKEN,
      MYSHOPIFY_DOMAIN: process.env.MYSHOPIFY_DOMAIN,
      SHOPIFY_API_VERSION: process.env.SHOPIFY_API_VERSION,
      NODE_ENV: process.env.NODE_ENV,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessages = error.errors.map(e => e.message).join(', ');
      console.error(`Environment validation failed: ${errorMessages}`);
      process.exit(1);
    }
    throw error;
  }
}

const env = loadEnvironment();
export default env;