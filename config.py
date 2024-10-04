import logging
import os
from openai import OpenAI
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# System prompt for the AI assistant
FUNCTION_CALL_SYSTEM_PROMPT = """
You are an AI assistant that helps users interact with the Neon API.
Your task is to interpret user queries and use the available tools to perform actions when necessary.
If a user's request requires an action, use the appropriate function call.
Don't fill optional parameters values if not provided by the user.
If the query cannot be answered based on the available tools, explain that to the user.
For complex tasks or when dependencies are involved:
1. If a required parameter is missing and a function exists to retrieve it, run that function first.
2. If multiple options are available for a parameter, propose these options to the user and ask for their preference.
3. Break down complex tasks into smaller, manageable steps and guide the user through each step.
4. Always consider the context and previous interactions in the conversation history when making decisions or suggestions.
"""

NATURAL_LANGUAGE_RESPONSE_SYSTEM_PROMPT = """
Provide a natural language response summarizing the result in a user-friendly manner. 
Only provide the necessary information. Do not display the entire result unless specifically asked. 
Example: 'The project was created successfully.'
"""

# Chat model to be used
CHAT_MODEL = "gpt-4o-mini"

# Function calling model to be used
FUNCTION_CALL_MODEL = "gpt-4o"

def get_openai_client() -> OpenAI:
    """
    Returns an instance of the OpenAI client initialized with the API key from environment variables.
    """
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize OpenAI client
client = get_openai_client()