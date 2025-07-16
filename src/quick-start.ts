import 'dotenv/config';
import { getBearerTokenProvider, DefaultAzureCredential } from '@azure/identity';
import { AIProjectClient } from '@azure/ai-projects';


const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
const deployment = process.env.AZURE_OPENAI_API_DEPLOYMENT_NAME;
const apiVersion = process.env.AZURE_OPENAI_API_VERSION;

if (!endpoint) {
    throw new Error('PROJECT_ENDPOINT environment variable is required');
}

if (!deployment) {
    throw new Error('AZURE_OPENAI_API_DEPLOYMENT_NAME environment variable is required');
}

const credentials = new DefaultAzureCredential();
const azureADTokenProvider = getBearerTokenProvider(
    credentials,
    'https://cognitiveservices.azure.com/.default'
);

// Create an Azure OpenAI Client
const project = new AIProjectClient(endpoint, credentials);

async function main() {
    console.log(`Starting inference...`);
    console.log(`Deployment: ${deployment}`);
    console.log(`API Version: ${apiVersion}`);

    const client = await project.inference.azureOpenAI({
        // The API version should match the version of the Azure OpenAI resource
        apiVersion: "2024-12-01-preview"
    });

    console.log(`Client created`);
    console.log(`Creating chat completion...`);


    // Create a chat completion
    const chatCompletion = await client.chat.completions.create({
        model: deployment!,
        messages: [
            { role: "system", content: "You are a helpful writing assistant" },
            { role: "user", content: "Write me a poem about flowers" },
        ],
    });
    console.log(`\n==================== 🌷SUCCESS ====================\n`);
    console.log(chatCompletion.choices[0].message.content);
}

main().catch(console.error);