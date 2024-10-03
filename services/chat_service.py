import os
from pydantic import BaseModel
from typing import Dict, Any, Optional, Tuple
import json
import logging
import uuid
import decimal

from utils.tools import tools
from services.neon_service import execute_api_call, get_current_user_info
from config import client, SYSTEM_PROMPT, CHAT_MODEL, FUNCTION_CALL_MODEL
from db import ChatDB

# Configure logging
logger = logging.getLogger(__name__)

# Initialize ChatDB
chat_db = ChatDB(db_url=os.getenv('DATABASE_URL'))

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    action_result: Optional[Dict[str, Any]] = None

class NewChatResponse(BaseModel):
    chat_id: str

def generate_natural_language_response(user_query: str, response_content: str) -> str:
    return client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Provide a natural language response summarizing the result in a user-friendly manner. Only provide the necessary information. Do not display the entire result unless specifically asked. Example: 'The project was created successfully.'"},
            {"role": "user", "content": f"User query: {user_query}, Function call: {response_content}"}
        ]
    ).choices[0].message.content

def convert_decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def chat(user_query: str, neon_api_key: str, chat_id: str) -> Dict[str, Any]:
    try:
        # Get chat history
        messages = chat_db.get_all_chat_history(chat_id)
        messages = [msg for msg in messages if msg.get('role') and msg.get('content')]
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
            {"role": "user", "content": f"User query: {user_query}"}
        ]

        # Process the user query
        response = client.chat.completions.create(model=FUNCTION_CALL_MODEL, messages=messages, tools=tools)
        assistant_message = response.choices[0].message

        chat_db.update_chat_history(chat_id, "user", user_query, is_function_call=False)
        
        # Extract tool call from assistant message
        tool_call = None

        if assistant_message.tool_calls:
            logger.info(f"assistant_message: {assistant_message.tool_calls}")
            tool_call = assistant_message.tool_calls[0]
        elif assistant_message.content:
            if assistant_message.content.startswith("Function call:"):
                parts = assistant_message.content.split(", Arguments: ")
                if len(parts) == 2:
                    function_name = parts[0].replace("Function call: ", "")
                    function_args = json.loads(parts[1])
                    function_args['neon_api_key'] = neon_api_key
                    tool_call = type('ToolCall', (), {'function': type('Function', (), {'name': function_name, 'arguments': json.dumps(function_args)})})()()
        
        response_dict = {}

        # Execute tool call if it exists
        if tool_call:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            # Pass messages to execute_api_call
            result = execute_api_call(function_name, neon_api_key=neon_api_key, messages=messages, **function_args)
            response_content = f"Executed {function_name} with result: {result}"
            
            natural_language_response = generate_natural_language_response(user_query, response_content)
            response_dict["response"] = natural_language_response
            
            chat_db.update_chat_history(chat_id, "assistant", f"Action result: {json.dumps(result, default=convert_decimal_to_float)}", True)
        else:
            response_dict["response"] = assistant_message.content or "No specific content provided."
        
        chat_db.update_chat_history(chat_id, "assistant", response_dict["response"], False)
        
        return response_dict
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        error_message = f"An error occurred: {str(e)}"
        response_dict["response"] = generate_natural_language_response(user_query, error_message)
    finally:
        return response_dict

def create_new_chat_session(neon_api_key: str) -> str:
    chat_id = str(uuid.uuid4())
    user_id = get_current_user_info(neon_api_key)
    chat_db.create_chat(chat_id, user_id)
    return chat_id
