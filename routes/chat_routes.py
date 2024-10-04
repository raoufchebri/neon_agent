import os
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Header, Path, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.chat_service import chat, create_new_chat_session
from models import ChatRequest, ChatResponse, NewChatResponse
import logging
from db import ChatDB
from models import ChatInfo
chat_db = ChatDB(db_url=os.getenv('DATABASE_URL'))

from services.neon_service import get_current_user_info

# Configure logging
logger = logging.getLogger(__name__)

# Define router
router = APIRouter()

security = HTTPBearer()

@router.post("/chats/{chat_id}", response_model=ChatResponse)
async def chat_endpoint(chat_id: str, request: ChatRequest = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Process a chat request and return a response.

    This endpoint accepts a user query, processes it using the AI assistant,
    and returns the assistant's response along with any action results from
    Neon API calls.

    Args:
        chat_id (str): The ID of the chat session.
        request (ChatRequest): The chat request containing the user's query.
        credentials (HTTPAuthorizationCredentials): The credentials containing the API key.

    Returns:
        ChatResponse: The assistant's response and any action results.

    Raises:
        HTTPException: If an error occurs during processing.
    """
    logger.info(f"Received chat request: {request}")
    
    neon_api_key = credentials.credentials
    if not neon_api_key:
        logger.error("Invalid or missing API key")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    logger.info(f"Processing chat request for chat_id: {chat_id}")
    response = chat(request.query, neon_api_key, chat_id)
    logger.info(f"Response dictionary: {response}")
    
    if response.get("response") is None:
        logger.error("The 'response' field is None")
        raise HTTPException(status_code=500, detail="The 'response' field is None")
    
    if "error" in response:
        logger.error(f"Error in chat response: {response['error']}")
        raise HTTPException(status_code=500, detail=response["error"])
    
    logger.info(f"Returning chat response: {response}")
    return ChatResponse(**response)

@router.get("/chats/{chat_id}/messages", response_model=List[Dict[str, str]])
async def get_chat_messages(chat_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Retrieve all messages for a specific chat session.

    This endpoint fetches the chat history for the given chat_id from the database.

    Args:
        chat_id (str): The ID of the chat session.
        credentials (HTTPAuthorizationCredentials): The credentials containing the API key.

    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing 'role' and 'content' of a message.

    Raises:
        HTTPException: If an error occurs during the retrieval process or if the chat_id is invalid.
    """
    neon_api_key = credentials.credentials
    if not neon_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    try:
        # Assuming chat_db is an instance of ChatDB that's accessible here
        messages = chat_db.get_chat_history(chat_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Chat not found or no messages available")
        return messages
    except Exception as e:
        logger.error(f"Error retrieving chat messages for chat_id {chat_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve chat messages")


@router.post("/chat/new", response_model=NewChatResponse)
async def create_new_chat(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Create a new chat session and return a unique chat ID.

    This endpoint generates a new unique chat ID for a new conversation.
    The client can use this ID in subsequent requests to maintain context.

    Args:
        credentials (HTTPAuthorizationCredentials): The credentials containing the API key.

    Returns:
        NewChatResponse: A dictionary containing the new chat ID.

    Raises:
        HTTPException: If an error occurs during the creation of the chat ID.
    """
    neon_api_key = credentials.credentials
    if not neon_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    try:
        chat_id = create_new_chat_session(neon_api_key=neon_api_key)
        return NewChatResponse(chat_id=chat_id)
    except Exception as e:
        logger.error(f"Error creating new chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create new chat")
    

@router.get("/chats", response_model=List[ChatInfo])
async def get_chats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Retrieve all chat sessions for the current user.

    This endpoint uses the provided Neon API key from the authorization header
    to get the user's ID, then queries the database for all chat sessions
    associated with that user.

    Args:
        credentials (HTTPAuthorizationCredentials): The credentials containing the API key.

    Returns:
        List[ChatInfo]: A list of ChatInfo objects, each containing a chat_id.

    Raises:
        HTTPException: If an error occurs during the retrieval process.
    """
    try:
        neon_api_key = credentials.credentials
        if not neon_api_key:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        user_id = get_current_user_info(neon_api_key)
        logger.info(f"User ID: {user_id}")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired Neon API key")

        chats = chat_db.get_user_chats(user_id)
        return [ChatInfo(chat_id=chat_id) for chat_id in chats]
    except Exception as e:
        logger.error(f"Error retrieving user chats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve user chats")

