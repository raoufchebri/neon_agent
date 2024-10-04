from typing import List, Dict, Any, Optional
import json
import decimal
from config import FUNCTION_CALL_MODEL, client, FUNCTION_CALL_SYSTEM_PROMPT, CHAT_MODEL, NATURAL_LANGUAGE_RESPONSE_SYSTEM_PROMPT
from services.neon_service import execute_api_call
from db import ChatDB
import os

chat_db = ChatDB(db_url=os.getenv('DATABASE_URL'))

def generate_natural_language_response(user_query: str, response_content: str) -> str:
    return client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": NATURAL_LANGUAGE_RESPONSE_SYSTEM_PROMPT},
            {"role": "user", "content": f"User query: {user_query}, Function call: {response_content}"}
        ]
    ).choices[0].message.content

def convert_decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def prepare_chat_history(chat_db, chat_id: str, user_query: str) -> List[Dict[str, str]]:
    messages = chat_db.get_all_chat_history(chat_id)
    messages = [msg for msg in messages if msg.get('role') and msg.get('content')]
    return [
        {"role": "system", "content": FUNCTION_CALL_SYSTEM_PROMPT},
        *messages,
        {"role": "user", "content": f"User query: {user_query}"}
    ]

def get_assistant_response(client, messages: List[Dict[str, str]], tools) -> Any:
    response = client.chat.completions.create(model=FUNCTION_CALL_MODEL, messages=messages, tools=tools)
    return response.choices[0].message

def extract_tool_call(assistant_message: Any, neon_api_key: str) -> Optional[Any]:
    if assistant_message.tool_calls:
        return assistant_message.tool_calls[0]
    elif assistant_message.content and assistant_message.content.startswith("Function call:"):
        return parse_function_call(assistant_message.content, neon_api_key)
    return None

def parse_function_call(content: str, neon_api_key: str) -> Any:
    parts = content.split(", Arguments: ")
    if len(parts) == 2:
        function_name = parts[0].replace("Function call: ", "")
        function_args = json.loads(parts[1])
        function_args['neon_api_key'] = neon_api_key
        return type('ToolCall', (), {'function': type('Function', (), {'name': function_name, 'arguments': json.dumps(function_args)})})()()
    return None

def handle_tool_call(tool_call: Any, neon_api_key: str, messages: List[Dict[str, str]], user_query: str) -> str:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    function_call_result = execute_api_call(function_name, neon_api_key=neon_api_key, messages=messages, **function_args)
    response_content = f"Executed {function_name} with result: {function_call_result}"
    natural_language_response = generate_natural_language_response(user_query, response_content)
    return natural_language_response, function_call_result