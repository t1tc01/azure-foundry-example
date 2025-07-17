import { DefaultAzureCredential } from "@azure/identity";
import { AIProjectClient } from "@azure/ai-projects";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
const deployment = process.env.AZURE_OPENAI_API_DEPLOYMENT_NAME;
const apiVersion = process.env.AZURE_OPENAI_API_VERSION;
const apiKey = process.env.AZURE_OPENAI_API_KEY;

if (!endpoint) {
    throw new Error('AZURE_OPENAI_ENDPOINT environment variable is required');
}

if (!deployment) {
    throw new Error('AZURE_OPENAI_API_DEPLOYMENT_NAME environment variable is required');
}

const credential = new DefaultAzureCredential();
const client = new AIProjectClient(endpoint, credential);

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
 * Main function to demonstrate basic chat with agent functionality
 */
async function main() {
    try {
        // Create an Agent
        const agent = await client.agents.createAgent(deployment!);
        console.log(`\n==================== 🕵️  POEM AGENT ====================`);

        // Create a thread and message
        const thread = await client.agents.threads.create();
        const prompt = 'Write me a poem about flowers';
        console.log(`\n---------------- 📝 User Prompt ---------------- \n${prompt}`);
        await client.agents.messages.create(thread.id, 'user', prompt);

        // Create run
        let run = await client.agents.runs.create(thread.id, agent.id);

        // Wait for run to complete
        console.log(`\n---------------- 🚦 Run Status ----------------`);
        while (['queued', 'in_progress', 'requires_action'].includes(run.status)) {
            // Avoid adding a lot of messages to the console
            await new Promise((resolve) => setTimeout(resolve, 1000));
            run = await client.agents.runs.get(thread.id, run.id);
            console.log(`Run status: ${run.status}`);
        }

        console.log('\n---------------- 📊 Token Usage ----------------');
        console.table([run.usage]);

        const messagesIterator = await client.agents.messages.list(thread.id);
        const assistantMessage = await getAssistantMessage(messagesIterator);
        console.log('\n---------------- 💬 Response ----------------');
        printAssistantMessage(assistantMessage);

        // Clean up
        console.log(`\n---------------- 🧹 Clean Up Poem Agent ----------------`);
        await client.agents.deleteAgent(agent.id);
        console.log(`Deleted Agent, Agent ID: ${agent.id}`);

    } catch (error) {
        console.error('Error in chat agent demo:', error);
        process.exit(1);
    }
}

// Run the main function
if (require.main === module) {
    main().catch(console.error);
}
