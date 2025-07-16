# azure-foundry-example

A TypeScript example project demonstrating how to use Azure OpenAI services with the Azure AI Projects SDK.

## Prerequisites

- Node.js (version 18 or higher)
- npm or yarn package manager
- Azure subscription with OpenAI service enabled
- Azure CLI (for authentication)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd azure-foundry-example
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## Configuration

1. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following variables:
   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_DEPLOYMENT_NAME=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   ```

2. **Azure Authentication:**
   This project uses `DefaultAzureCredential` for authentication. You can authenticate using one of these methods:
   
   - **Azure CLI (Recommended for development):**
     ```bash
     az login
     ```
   
   - **Environment Variables:**
     ```bash
     export AZURE_CLIENT_ID=your-client-id
     export AZURE_CLIENT_SECRET=your-client-secret
     export AZURE_TENANT_ID=your-tenant-id
     ```
   
   - **Managed Identity:** (when running on Azure)

## Running the Project

### Quick Start Example

Run the basic OpenAI chat completion example:

```bash
npm run quick-start
```

### Available Scripts

- `npm run quick-start` - Run the quick start example
- `npm test` - Run tests (currently not implemented)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


