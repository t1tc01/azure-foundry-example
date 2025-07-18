import os

from dotenv import load_dotenv

# Load .env file from the project root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


class Config:
    def __init__(self):

        self.MINIMUM_SUPPORTED_AZURE_OPENAI_PREVIEW_API_VERSION = "2024-02-15-preview"

        # Azure OpenAI Integration Settings
        self.AZURE_OPENAI_RESOURCE = os.environ.get("AZURE_OPENAI_RESOURCE")
        self.AZURE_OPENAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL")
        self.AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
        self.AZURE_OPENAI_TEMPERATURE = os.environ.get("AZURE_OPENAI_TEMPERATURE", 0)
        self.AZURE_OPENAI_TOP_P = os.environ.get("AZURE_OPENAI_TOP_P", 1.0)
        self.AZURE_OPENAI_MAX_TOKENS = os.environ.get("AZURE_OPENAI_MAX_TOKENS", 1000)
        self.AZURE_OPENAI_STOP_SEQUENCE = os.environ.get("AZURE_OPENAI_STOP_SEQUENCE")
        self.AZURE_OPENAI_SYSTEM_MESSAGE = os.environ.get(
            "AZURE_OPENAI_SYSTEM_MESSAGE",
            "You are an AI assistant that helps people find information.",
        )
        self.AZURE_OPENAI_PREVIEW_API_VERSION = os.environ.get(
            "AZURE_OPENAI_PREVIEW_API_VERSION",
            self.MINIMUM_SUPPORTED_AZURE_OPENAI_PREVIEW_API_VERSION,
        )
        self.AZURE_OPENAI_STREAM = os.environ.get("AZURE_OPENAI_STREAM", "true")
        self.AZURE_OPENAI_EMBEDDING_ENDPOINT = os.environ.get(
            "AZURE_OPENAI_EMBEDDING_ENDPOINT"
        )
        self.AZURE_OPENAI_EMBEDDING_KEY = os.environ.get("AZURE_OPENAI_EMBEDDING_KEY")
        self.AZURE_OPENAI_EMBEDDING_NAME = os.environ.get(
            "AZURE_OPENAI_EMBEDDING_NAME", ""
        )

        self.SHOULD_STREAM = (
            True if self.AZURE_OPENAI_STREAM.lower() == "true" else False
        )


        # Azure AI Project (Foundry) configuration
        self.USE_AI_PROJECT_CLIENT = (
            os.getenv("USE_AI_PROJECT_CLIENT", "False").lower() == "true"
        )
        self.AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_AGENT_ENDPOINT")
        
        # SQL Database configuration
        self.SQL_DATABASE = os.getenv("SQLDB_DATABASE")
        self.SQL_SERVER = os.getenv("SQLDB_SERVER")
        self.SQL_USERNAME = os.getenv("SQLDB_USERNAME")
        self.SQL_PASSWORD = os.getenv("SQLDB_PASSWORD")
        self.ODBC_DRIVER = "{ODBC Driver 18 for SQL Server}"
        self.MID_ID = os.getenv("SQLDB_USER_MID")

        # SQL System Prompt
        self.SQL_SYSTEM_PROMPT = os.getenv("SQL_SYSTEM_PROMPT")


config = Config()