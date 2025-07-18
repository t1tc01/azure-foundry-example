import logging
from typing import Annotated
import openai
from azure.ai.agents.models import (
    Agent,
    AzureAISearchQueryType,
    AzureAISearchTool,
    MessageRole,
)
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.projects import AIProjectClient
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from backend.common.config import config
from backend.services.sqldnb_service import get_connection


class ChatWithDataPlugin:
    @kernel_function(
        name="GreetingsResponse",
        description="Respond to any greeting or general questions",
    )
    async def greeting(
        self, input: Annotated[str, "the question"]
    ) -> Annotated[str, "The output is a string"]:
        """
        Simple greeting handler using Azure OpenAI.
        """
        try:
            if config.USE_AI_PROJECT_CLIENT:
                client = self.get_project_openai_client()

            else:
                client = self.get_openai_client()

            completion = client.chat.completions.create(
                model=config.AZURE_OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant to respond to greetings or general questions.",
                    },
                    {"role": "user", "content": input},
                ],
                temperature=0,
                top_p=1,
                n=1,
            )

            answer = completion.choices[0].message.content
        except Exception as e:
            answer = f"Error retrieving greeting response: {str(e)}"
        return answer
    
    
    @kernel_function(
        name="ChatWithSQLDatabase",
        description="Given a query about client assets, investments and scheduled meetings (including upcoming or next meeting dates/times), get details from the database based on the provided question and client id",
    )
    async def get_SQL_Response(
        self,
        input: Annotated[str, "the question"],
        invoice_id: Annotated[str, "the invoice_id"],
    ) -> Annotated[str, "The output is a string"]:
        """
        Dynamically generates a T-SQL query using the Azure OpenAI chat endpoint
        and then executes it against the SQL database.
        """
        if not invoice_id or not invoice_id.strip():
            return "Error: invoice_id is required"

        if not input or not input.strip():
            return "Error: Query input is required"

        clientid = invoice_id
        query = input

        # Retrieve the SQL prompt from environment variables (if available)
        sql_prompt = config.SQL_SYSTEM_PROMPT
        if sql_prompt:
            sql_prompt = sql_prompt.replace("{query}", query).replace(
                "{invoice_id}", clientid
            )
        else:
            # Fallback prompt if not set in environment
            sql_prompt = f"""Generate a valid T-SQL query to find {query} for tables and columns provided below:
            1. Table: invoices
            Columns: id, invoiceName, updateHistory
            Assets table has snapshots of values by date. Do not add numbers across different dates for total values.
            Do not use client name in filters.
            Do not include assets values unless asked for.
            ALWAYS use invoices.id = {clientid} in the query filter.
            ALWAYS select invoiceName (Column: invoiceName) in the query.
            Query filters are IMPORTANT. Add filters if needed.
            Only return the generated SQL query. Do not return anything else.
            Just using SELECT id, "invoiceName" from invoices where invoices.id = {clientid} is enough.
            """

        try:
            if config.USE_AI_PROJECT_CLIENT:
                client = self.get_project_openai_client()

            else:
                # Initialize the Azure OpenAI client
                client = self.get_openai_client()

            completion = client.chat.completions.create(
                model=config.AZURE_OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": sql_prompt},
                ],
                temperature=0,
                top_p=1,
                n=1,
            )

            sql_query = completion.choices[0].message.content
            # logging.info(f"SQL Query: {sql_query}")

            # # Remove any triple backticks if present
            # sql_query = sql_query.replace("```sql", "").replace("```", "")

            # # print("Generated SQL:", sql_query)

            # conn = get_connection()
            # # conn = pyodbc.connect(connectionString)
            # cursor = conn.cursor()
            # cursor.execute(sql_query)

            # rows = cursor.fetchall()
            # if not rows:
            #     answer = "No data found for that client."
            # else:
            #     answer = ""
            #     for row in rows:
            #         answer += str(row) + "\n"

            # conn.close()
            # answer = answer[:20000] if len(answer) > 20000 else answer
            # logging.info(f"SQL Response: {answer}")

            answer = sql_query
        except Exception as e:
            answer = f"Error retrieving data from SQL: {str(e)}"
        return answer

    def get_openai_client(self):
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        openai_client = openai.AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=config.AZURE_OPENAI_PREVIEW_API_VERSION,
        )
        return openai_client
    
    def get_project_openai_client(self):
        project = AIProjectClient(
            endpoint=config.AI_PROJECT_ENDPOINT, credential=DefaultAzureCredential()
        )
        openai_client = project.inference.get_azure_openai_client(
            api_version=config.AZURE_OPENAI_PREVIEW_API_VERSION
        )
        return openai_client