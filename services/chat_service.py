from pydantic import BaseModel
from typing import Dict, Any, Optional, Tuple
import json
import logging
import uuid

from utils.tools import tools
from utils.neon_api import execute_api_call
from config import client, SYSTEM_PROMPT, CHAT_MODEL, FUNCTION_CALL_MODEL
from db import ChatDB

# Configure logging
logger = logging.getLogger(__name__)

# Initialize ChatDB
chat_db = ChatDB()

class ChatRequest(BaseModel):
    query: str
    neon_api_key: str
    chat_id: str

class ChatResponse(BaseModel):
    response: str
    action_result: Optional[Dict[str, Any]] = None

class NewChatResponse(BaseModel):
    chat_id: str

def prepare_messages(query: str, chat_id: str) -> list:
    messages = chat_db.get_chat_history(chat_id)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
        {"role": "user", "content": f"User query: {query}"}
    ]

def handle_tool_call(tool_call, neon_api_key: str, chat_id: str) -> None:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    function_args['neon_api_key'] = neon_api_key
    chat_db.update_chat_history(chat_id, "assistant", f"Function call: {function_name}, Arguments: {json.dumps(function_args)}")

def process_assistant_content(content: str, neon_api_key: str, chat_id: str) -> Optional[Any]:
    if content.startswith("Function call:"):
        parts = content.split(", Arguments: ")
        if len(parts) == 2:
            function_name = parts[0].replace("Function call: ", "")
            function_args = json.loads(parts[1])
            function_args['neon_api_key'] = neon_api_key
            return type('ToolCall', (), {'function': type('Function', (), {'name': function_name, 'arguments': json.dumps(function_args)})})()
    chat_db.update_chat_history(chat_id, "assistant", content)
    return None

def process_user_query(query: str, neon_api_key: str, chat_id: str) -> Tuple[Any, Optional[Any]]:
    messages = prepare_messages(query, chat_id)
    response = client.chat.completions.create(model=FUNCTION_CALL_MODEL, messages=messages, tools=tools)
    assistant_message = response.choices[0].message
    chat_db.update_chat_history(chat_id, "user", query)
    
    tool_call = None
    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        handle_tool_call(tool_call, neon_api_key, chat_id)
    elif assistant_message.content:
        tool_call = process_assistant_content(assistant_message.content, neon_api_key, chat_id)

    return assistant_message, tool_call

def generate_natural_language_response(user_query: str, response_content: str) -> str:
    return client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "Provide a natural language response summarizing the result in a user-friendly manner. Only provide the necessary information. Do not display the entire result unless specifically asked. Example: 'The project was created successfully.'"},
            {"role": "user", "content": f"User query: {user_query}, Function call: {response_content}"}
        ]
    ).choices[0].message.content

def chat(user_query: str, neon_api_key: str, chat_id: str) -> Dict[str, Any]:
    try:
        assistant_message, tool_call = process_user_query(user_query, neon_api_key, chat_id)
        logger.info(f"Assistant message: {assistant_message}")
        
        response_content = getattr(assistant_message, 'content', None)
        action_result = None
        
        if response_content is None and tool_call:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            result = execute_api_call(function_name, neon_api_key=neon_api_key, **function_args)
            response_content = f"Executed {function_name} with result: {result}"
            action_result = result
            
            natural_language_response = generate_natural_language_response(user_query, response_content)
            
            # Update assistant message with natural language response and action result
            chat_db.update_chat_history(chat_id, "assistant", natural_language_response)
            chat_db.update_chat_history(chat_id, "assistant", f"Action result: {json.dumps(result)}")
            
            response_dict = {"response": natural_language_response}
        else:
            response_dict = {"response": response_content or "No specific content provided."}
            chat_db.update_chat_history(chat_id, "assistant", response_dict["response"])
        
        logger.info(f"Response content: {response_content}")
        return response_dict
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        return {"error": str(e)}

def create_new_chat_session() -> str:
    chat_id = str(uuid.uuid4())
    chat_db.create_chat(chat_id)
    return chat_id
