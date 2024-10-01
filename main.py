"""
Neon API Assistant

This module implements a FastAPI application that serves as an AI-powered assistant
for interacting with the Neon API. It uses OpenAI's GPT-4 model to interpret user
queries and execute corresponding Neon API calls.

Key Features:
- Natural language processing of user queries related to Neon API operations
- Execution of Neon API calls based on interpreted user intent
- Conversation history management for context-aware responses
- Error handling and informative responses

Dependencies:
- FastAPI: For creating the web API
- Pydantic: For request/response data validation
- OpenAI: For natural language processing using GPT-4
- Custom modules: tools.py and neon_api_specs.py for Neon API integration

Usage:
Run this file to start the FastAPI server. Send POST requests to the /chat endpoint
with a JSON body containing 'query' and 'neon_api_key' fields to interact with the assistant.

Environment Variables:
- OPENAI_API_KEY: Your OpenAI API key for authentication

License: MIT
Author: [Your Name/Organization]
Version: 1.0.0
"""

import json
import logging
import os
from typing import Dict, Any, Tuple, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from tools import tools
from neon_api_utils import execute_api_call

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str
    neon_api_key: str

class ChatResponse(BaseModel):
    response: str
    action_result: Optional[Dict[str, Any]] = None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation_history: Dict[str, list] = {"messages": []}

SYSTEM_PROMPT = """
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

CHAT_MODEL = "gpt-4o"

def prepare_messages(query: str) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history["messages"],
        {"role": "user", "content": f"User query: {query}"}
    ]

def handle_tool_call(tool_call, neon_api_key: str) -> None:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    function_args['neon_api_key'] = neon_api_key
    conversation_history["messages"].append({
        "role": "assistant",
        "content": f"Function call: {function_name}, Arguments: {json.dumps(function_args)}"
    })

def process_assistant_content(content: str, neon_api_key: str) -> Optional[Any]:
    if content.startswith("Function call:"):
        parts = content.split(", Arguments: ")
        if len(parts) == 2:
            function_name = parts[0].replace("Function call: ", "")
            function_args = json.loads(parts[1])
            function_args['neon_api_key'] = neon_api_key
            return type('ToolCall', (), {'function': type('Function', (), {'name': function_name, 'arguments': json.dumps(function_args)})})()
    conversation_history["messages"].append({"role": "assistant", "content": content})
    return None

def process_user_query(query: str, neon_api_key: str) -> Tuple[Any, Optional[Any]]:
    messages = prepare_messages(query)
    response = client.chat.completions.create(model=CHAT_MODEL, messages=messages, tools=tools)
    assistant_message = response.choices[0].message
    conversation_history["messages"].append({"role": "user", "content": query})
    
    tool_call = None
    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        handle_tool_call(tool_call, neon_api_key)
    elif assistant_message.content:
        tool_call = process_assistant_content(assistant_message.content, neon_api_key)

    return assistant_message, tool_call

def chat(user_query: str, neon_api_key: str) -> Dict[str, Any]:
    try:
        assistant_message, tool_call = process_user_query(user_query, neon_api_key)
        
        # Log the assistant message
        logger.info(f"Assistant message: {assistant_message}")
        
        response_content = getattr(assistant_message, 'content', None)
        
        # If the response content is None, check for tool call results
        if response_content is None and tool_call:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            result = execute_api_call(function_name, neon_api_key=neon_api_key, **function_args)
            response_content = f"Executed {function_name} with result: {result}"
            response_dict = {"response": response_content, "action_result": result}
        else:
            response_dict = {"response": response_content}
        
        # Log the response content
        logger.info(f"Response content: {response_content}")
        
        return response_dict
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        return {"error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat request and return a response.

    This endpoint accepts a user query, processes it using the AI assistant,
    and returns the assistant's response along with any action results from
    Neon API calls.

    Args:
        request (ChatRequest): The chat request containing the user's query and Neon API key.

    Returns:
        ChatResponse: The assistant's response and any action results.

    Raises:
        HTTPException: If an error occurs during processing.
    """
    response = chat(request.query, request.neon_api_key)
    
    # Log the response dictionary
    logger.info(f"Response dictionary: {response}")
    
    # Check if the response field is None
    if response.get("response") is None:
        logger.error("The 'response' field is None")
        raise HTTPException(status_code=500, detail="The 'response' field is None")
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    return ChatResponse(**response)