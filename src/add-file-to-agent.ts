import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";
import { AIProjectClient } from "@azure/ai-projects";
import * as fs from "fs";
import * as path from "path";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
const deployment = process.env.AZURE_OPENAI_API_DEPLOYMENT_NAME;

if (!endpoint) {
    throw new Error('AZURE_OPENAI_ENDPOINT environment variable is required');
}

if (!deployment) {
    throw new Error('AZURE_OPENAI_API_DEPLOYMENT_NAME environment variable is required');
}

const credentials = new DefaultAzureCredential();
const azureADTokenProvider = getBearerTokenProvider(
    credentials,
    'https://cognitiveservices.azure.com/.default'
);

// Create the AI Projects client
const client = new AIProjectClient(endpoint, credentials);

/**
 * Helper function to get assistant message from messages iterator
 */
async function getAssistantMessage(messagesIterator: any) {
    const messages = [];
    for await (const message of messagesIterator) {
        messages.push(message);
    }
    
    // Find the latest assistant message
    const assistantMessage = messages.find(msg => msg.role === 'assistant');
    return assistantMessage;
}

/**
 * Helper function to print assistant message content
 */
function printAssistantMessage(message: any) {
    if (message && message.content) {
        for (const contentItem of message.content) {
            if (contentItem.type === 'text') {
                console.log(contentItem.text.value);
            }
        }
    }
}

/**
 * Main function to demonstrate file agent functionality
 */
async function main() {
    try {
        // Upload a file named product_info_1.md
        console.log(`\n==================== 🕵️  FILE AGENT ====================`);
        const __dirname = path.dirname(require.main?.filename || __filename);
        const filePath = path.join(__dirname, '../data/product_info_1.md');
        
        if (!fs.existsSync(filePath)) {
            throw new Error(`File not found: ${filePath}`);
        }
        
        const fileStream = fs.createReadStream(filePath);
        
        const file = await client.agents.files.upload(fileStream, 'assistants', {
            fileName: 'product_info_1.md'
        });
        console.log(`Uploaded file, ID: ${file.id}`);
        
        const vectorStore = await client.agents.vectorStores.create({
            fileIds: [file.id],
            name: 'my_vectorstore'
        });
        
        console.log('\n---------------- 🗃️ Vector Store Info ----------------');
        console.table([
            {
                'Vector Store ID': vectorStore.id,
                'Usage (bytes)': vectorStore.usageBytes,
                'File Count': vectorStore.fileCounts?.total ?? 'N/A'
            }
        ]);

        // Create an Agent and a FileSearch tool
        const fileSearchTool = {
            type: 'file_search' as const,
            file_search: {
                vector_store_ids: [vectorStore.id]
            }
        };
        
        const fileAgent = await client.agents.createAgent(deployment!, {
            name: 'my-file-agent',
            instructions: 'You are a helpful assistant and can search information from uploaded files',
            tools: [fileSearchTool],
            toolResources: {
                fileSearch: {
                    vectorStoreIds: [vectorStore.id]
                }
            }
        });

        // Create a thread and message
        const fileSearchThread = await client.agents.threads.create({ 
            toolResources: {
                fileSearch: {
                    vectorStoreIds: [vectorStore.id]
                }
            }
        });
        
        const filePrompt = 'What are the steps to setup the TrailMaster X4 Tent?';
        console.log(`\n---------------- 📝 User Prompt ---------------- \n${filePrompt}`);
        
        await client.agents.messages.create(fileSearchThread.id, 'user', filePrompt);

        // Create run
        let fileSearchRun = await client.agents.runs.create(fileSearchThread.id, fileAgent.id).stream();

        console.log('\n---------------- 🤖 Processing... ----------------');
        for await (const eventMessage of fileSearchRun) {
            if (eventMessage.event === 'thread.run.completed') {
                console.log(`Run completed successfully`);
            }
            if (eventMessage.event === 'thread.run.failed') {
                console.log(`Run failed: ${eventMessage.data}`);
            }
        }

        const fileSearchMessagesIterator = await client.agents.messages.list(fileSearchThread.id);
        const fileAssistantMessage = await getAssistantMessage(fileSearchMessagesIterator);
        console.log(`\n---------------- 💬 Response ---------------- \n`);
        printAssistantMessage(fileAssistantMessage);

        // Clean up
        console.log(`\n---------------- 🧹 Clean Up File Agent ----------------`);
        await client.agents.vectorStores.delete(vectorStore.id);
        await client.agents.files.delete(file.id);
        await client.agents.deleteAgent(fileAgent.id);
        console.log(`Deleted VectorStore, File, and FileAgent. FileAgent ID: ${fileAgent.id}`);

    } catch (error) {
        console.error('Error in file agent demo:', error);
        process.exit(1);
    }
}

// Run the main function
if (require.main === module) {
    main().catch(console.error);
}

