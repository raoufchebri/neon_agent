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
with a JSON body containing 'query', 'neon_api_key', and 'chat_id' fields to interact with the assistant.

Environment Variables:
- OPENAI_API_KEY: Your OpenAI API key for authentication

License: MIT
Author: [Your Name/Organization]
Version: 1.0.0
"""

import logging
from fastapi import FastAPI
from config import app
from routes import chat_router  #

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include chat router
app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    ascii_art = """
       @@@@@@@@@@@@@@@@@@@@&&&&&&&%%                                                                                                                  
  @@@@@@@@@@@@@@@@@@@@&&&&&&&&&&%%%%#####                                                                                                             
 @@@@@@@@@@@@@@@@@@&&&&&&&&&&&&%%%%#######/                                                                                                           
@@@@@@                               ######                                                                                                           
@@@@@@                               ######                                                                                                           
@@@@@@                               ######            @@@@@@%          @@@@@    @@@@@@@@@@@@@@@@@@@        @@@@@@@@@@@@         @@@@@@          @@@@@
@@@@@@                 #####         ######            @@@@@@@@@        @@@@@    @@@@@@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@@@@@     @@@@@@@@@       @@@@@
@@@@&&               #########       ######            @@@@@@@@@@@%     @@@@@    @@@@@                 @@@@@@          @@@@@@    @@@@@@@@@@@     @@@@@
@@@&&&               ###########     ######            @@@@@@ @@@@@@@   @@@@@    @@@@@@@@@@@@@@@@@    @@@@@@            @@@@@@   @@@@@  @@@@@@@  @@@@@
@&&&&&               #############   ######            @@@@@@    @@@@@@.@@@@@    @@@@@@@@@@@@@@@@@    @@@@@@            @@@@@@   @@@@@    (@@@@@@@@@@@
&&&&&&               ######  ####### ######            @@@@@@      &@@@@@@@@@    @@@@@                 @@@@@@@        @@@@@@@    @@@@@       @@@@@@@@@
&&&&&&               ######    ############            @@@@@@         @@@@@@@    @@@@@@@@@@@@@@@@@@@%    @@@@@@@@@@@@@@@@@@@@      @@@@@         (@@@@@@
&&&&&&               ######      ##########                                                                   @@@@@@@@                                
&&&&&&               ######        #######                                                                                                            
&&&&&&&              ######                                                                                                                           
 &&&&&&&&&&&&&%%%%%#######                                                                                                                            
    &&&&&&&&&%%%%%######   
    """
    print(ascii_art)