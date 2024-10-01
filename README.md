# Neon API Assistant

## Overview

Neon API Assistant is a FastAPI application that serves as an AI-powered assistant for interacting with the Neon API. It leverages OpenAI's GPT-4 model to interpret user queries and execute corresponding Neon API calls.

## Key Features

- **Natural Language Processing**: Understands and processes user queries related to Neon API operations.
- **API Execution**: Executes Neon API calls based on interpreted user intent.
- **Conversation Management**: Maintains conversation history for context-aware responses.
- **Error Handling**: Provides informative responses and handles errors gracefully.

## Dependencies

- **FastAPI**: For creating the web API.
- **Pydantic**: For request/response data validation.
- **OpenAI**: For natural language processing using GPT-4.
- **Custom Modules**: `tools.py` and `neon_api_utils.py` for Neon API integration.

## Usage

Run the `main.py` file to start the FastAPI server. Send POST requests to the `/chat` endpoint with a JSON body containing `query` and `neon_api_key` fields to interact with the assistant.

### Example Request
json
{
"query": "Create a new project named 'MyProject'",
"neon_api_key": "your_neon_api_key"
}

### Example Response
json
{
"response": "Executed create_project with result: { ... }",
"action_result": { ... }
}

```
## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for authentication.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/neon_agent.git
    cd neon_agent
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your environment variables:
    ```sh
    export OPENAI_API_KEY=your_openai_api_key
    ```

5. Run the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

## API Endpoints

### POST /chat

Process a chat request and return a response.

#### Request Body

- `query` (string): The user's query.
- `neon_api_key` (string): The Neon API key for authentication.

#### Response

- `response` (string): The assistant's response.
- `action_result` (optional, dict): The result of any executed Neon API call.

## License

This project is licensed under the MIT License.

## Author

[Your Name/Organization]

## Version

1.0.0