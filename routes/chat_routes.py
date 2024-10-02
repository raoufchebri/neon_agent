from fastapi import APIRouter, HTTPException
from services.chat_service import chat, create_new_chat_session, ChatResponse, ChatRequest, NewChatResponse
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define router
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat request and return a response.

    This endpoint accepts a user query, processes it using the AI assistant,
    and returns the assistant's response along with any action results from
    Neon API calls.

    Args:
        request (ChatRequest): The chat request containing the user's query, Neon API key, and chat ID.

    Returns:
        ChatResponse: The assistant's response and any action results.

    Raises:
        HTTPException: If an error occurs during processing.
    """
    response = chat(request.query, request.neon_api_key, request.chat_id)
    logger.info(f"Response dictionary: {response}")
    
    if response.get("response") is None:
        logger.error("The 'response' field is None")
        raise HTTPException(status_code=500, detail="The 'response' field is None")
    
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    return ChatResponse(**response)

@router.post("/chat/new", response_model=NewChatResponse)
async def create_new_chat():
    """
    Create a new chat session and return a unique chat ID.

    This endpoint generates a new unique chat ID for a new conversation.
    The client can use this ID in subsequent requests to maintain context.

    Returns:
        NewChatResponse: A dictionary containing the new chat ID.

    Raises:
        HTTPException: If an error occurs during the creation of the chat ID.
    """
    try:
        chat_id = create_new_chat_session()
        return NewChatResponse(chat_id=chat_id)
    except Exception as e:
        logger.error(f"Error creating new chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create new chat")