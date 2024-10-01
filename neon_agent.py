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
import os
from openai import OpenAI
from tools import tools
from neon_api_utils import execute_api_call
from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException

app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    neon_api_key: str

class ChatResponse(BaseModel):
    response: str
    action_result: Optional[Dict[str, Any]] = None

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get Neon API key from environment variables
NEON_API_KEY = os.getenv("NEON_API_KEY")

conversation_history = {"messages": []}

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

def process_user_query(query, neon_api_key):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history["messages"],
        {"role": "user", "content": f"User query: {query}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools
    )

    assistant_message = response.choices[0].message
    conversation_history["messages"].append({"role": "user", "content": query})

    if assistant_message.tool_calls:
        return handle_tool_call(assistant_message.tool_calls[0])
    elif assistant_message.content:
        return assistant_message, process_assistant_content(assistant_message.content, neon_api_key)

    return assistant_message, None

def handle_tool_call(tool_call):
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    conversation_history["messages"].append({
        "role": "assistant",
        "content": f"Function call: {function_name}, Arguments: {json.dumps(function_args)}"
    })
    return None, tool_call

def chat(user_query, neon_api_key):
    try:
        assistant_message, tool_call = process_user_query(user_query, neon_api_key)
        
        response_dict = {
            "response": getattr(assistant_message, 'content', "No response content available")
        }
        
        if tool_call:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_args['neon_api_key'] = neon_api_key
            result = execute_api_call(function_name, **function_args)
            response_dict["action_result"] = result
        
        return response_dict
    except Exception as e:
        return {"error": str(e)}

def process_assistant_content(content, neon_api_key):
    if content.startswith("Function call:"):
        parts = content.split(", Arguments: ")
        if len(parts) == 2:
            function_name = parts[0].replace("Function call: ", "")
            function_args = json.loads(parts[1])
            function_args['neon_api_key'] = neon_api_key
            return type('ToolCall', (), {'function': type('Function', (), {'name': function_name, 'arguments': json.dumps(function_args)})})()
    
    conversation_history["messages"].append({"role": "assistant", "content": content})
    return None

# def main():
#     while True:
#         user_input = input("User: ")
#         if user_input.lower() == 'exit':
#             break
#         response = chat(user_input, NEON_API_KEY)
#         print(ChatResponse(**response))

# if __name__ == "__main__":
#     main()

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
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    return ChatResponse(**response)
