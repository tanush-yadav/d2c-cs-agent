# Contributing Guidelines

Thank you for your interest in contributing to the Shopify MCP Server! We welcome contributions from everyone.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/shopify-mcp-server.git`
3. Install dependencies: `npm install`
4. Create a new branch for your changes: `git checkout -b your-feature-branch`
5. Make your changes
6. Test your changes: `npm test`

## Development Setup

To set up your development environment:

1. Copy `.env.example` to `.env` and fill in the required values
   ```
   SHOPIFY_ACCESS_TOKEN=your_access_token
   MYSHOPIFY_DOMAIN=your-shop.myshopify.com
   ```

2. Build the project:
   ```
   npm run build
   ```

3. Run in development mode:
   ```
   npm run dev
   ```

## Code Style

We use ESLint and Prettier to maintain code quality. Before submitting your changes:

1. Run the linter: `npm run lint`
2. Fix linting issues: `npm run lint:fix`
3. Format your code: `npm run format`

## Project Structure

The project follows a modular architecture:

- `src/index.ts`: Main entry point
- `src/config/`: Configuration files
- `src/tools/`: MCP tool implementations
- `src/ShopifyClient/`: Shopify API client
- `src/utils/`: Utility functions
- `src/__tests__/`: Test files

## Adding New Tools

When adding new tools:

1. Create or extend the appropriate file in the `src/tools/` directory
2. Register the tool in the appropriate tool registry file
3. Add tests for your new tool
4. Update documentation if necessary

## Testing

We use Jest for testing. Run tests with:

```
npm test
```

For test coverage:

```
npm test -- --coverage
```

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Add/update tests as necessary
3. Update documentation if needed
4. Ensure all tests pass
5. Submit your pull request with a clear description of the changes

## Code of Conduct

Please note that this project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

## License

By contributing to the Shopify MCP Server, you agree that your contributions will be licensed under the project's MIT License.