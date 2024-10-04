import json
import os
from pydantic import BaseModel
from typing import Dict, Any
import logging
import uuid

from utils.tools import tools
from services.neon_service import get_current_user_info
from config import client
from db import ChatDB
from utils.chat_utils import (
    generate_natural_language_response,
    convert_decimal_to_float,
    handle_tool_call,
    prepare_chat_history,
    get_assistant_response,
    extract_tool_call
)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize ChatDB
chat_db = ChatDB(db_url=os.getenv('DATABASE_URL'))

def chat(user_query: str, neon_api_key: str, chat_id: str) -> Dict[str, Any]:
    try:
        # Retrieve and prepare chat history
        messages = prepare_chat_history(chat_db, chat_id, user_query)

        # Process the user query and get the assistant's response
        assistant_message = get_assistant_response(client, messages, tools)

        # Collect chat history entries
        chat_entries = []

        # Add user's query to chat entries
        chat_entries.append({
            "role": "user",
            "content": user_query,
            "is_function_call": False
        })

        # Determine if a tool call is needed
        tool_call = extract_tool_call(assistant_message, neon_api_key)

        # Prepare the response dictionary
        response_dict = {}

        # Execute tool call if it exists
        if tool_call:
            response_dict["response"], function_call_result = handle_tool_call(tool_call, neon_api_key, messages, user_query)
            chat_entries.append({
                "role": "assistant",
                "content": f"Action result: {json.dumps(function_call_result, default=convert_decimal_to_float)}",
                "is_function_call": True
            })
        else:
            response_dict["response"] = assistant_message.content or "No specific content provided."

        # Add assistant's response to chat entries
        chat_entries.append({
            "role": "assistant",
            "content": response_dict["response"],
            "is_function_call": False
        })

        # Update chat history with all entries

    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        error_message = f"An error occurred: {str(e)}"
        response_dict["response"] = generate_natural_language_response(user_query, error_message)
        chat_entries.append({
            "role": "assistant",
            "content": response_dict["response"],
            "is_function_call": False
        })
    finally:
        chat_db.update_chat_history(chat_id, chat_entries)
        return response_dict

def create_new_chat_session(neon_api_key: str) -> str:
    chat_id = str(uuid.uuid4())
    user_id = get_current_user_info(neon_api_key)
    chat_db.create_chat(chat_id, user_id)
    return chat_id
