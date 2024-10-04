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

## Local Usage

### Prerequisites

- Python 3.7+
- PostgreSQL database
- OpenAI API key
- Neon API key

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/raoufchebri/neon_agent.git
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

4. Copy the `.env.example` file to a new `.env` file:
    ```sh
    cp .env.example .env
    ```

5. Set up your environment variables in the `.env` file:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    NEON_API_KEY=your_neon_api_key
    DATABASE_URL=your_database_url
    ```

6. Run the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

### Example Usage

1. **Create a New Chat Session**

   Send a POST request to the `/chat/new` endpoint to create a new chat session and get a unique `chat_id`.

   ```sh
   curl -X POST "http://127.0.0.1:8000/chat/new"
   ```

   Example Response:
   ```json
   {
       "chat_id": "your_generated_chat_id"
   }
   ```

2. **Interact with the Assistant**

   Send a POST request to the `/chat` endpoint with a JSON body containing `query`, `neon_api_key`, and `chat_id` fields to interact with the assistant.

   ```sh
   curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d '{
       "query": "Create a new project named 'MyProject'",
       "neon_api_key": "your_neon_api_key",
       "chat_id": "your_generated_chat_id"
   }'
   ```

   Example Response:
   ```json
   {
       "response": "Executed create_project with result: { ... }",
       "action_result": { ... }
   }
   ```

## Deploying on Koyeb

### Prerequisites

- Koyeb account
- GitHub repository for your project

### Steps

1. **Fork the Repository**: Fork this repository to your GitHub account.

2. **Add the Deploy to Koyeb Button**: Add the following Markdown snippet to your repository's README file to enable one-click deployment to Koyeb:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&builder=buildpack&repository=github.com/raoufchebri/neon_agent&branch=main&name=neon-api-assistant)

3. **Configure Environment Variables**: In the Koyeb dashboard, set the following environment variables for your service:
    - `OPENAI_API_KEY`
    - `NEON_API_KEY`
    - `DATABASE_URL`

4. **Deploy the Application**: Click the "Deploy to Koyeb" button in your repository's README file. This will take you to the Koyeb deployment page where you can configure and deploy your application.

5. **Monitor Deployment**: Follow the deployment progress in the Koyeb dashboard. Once deployed, your application will be accessible via the provided URL.

## API Endpoints

### POST /chat/new

Create a new chat session and return a unique chat ID.

#### Response

- `chat_id` (string): The unique chat ID for the new session.

### POST /chat

Process a chat request and return a response.

#### Request Body

- `query` (string): The user's query.
- `neon_api_key` (string): The Neon API key for authentication.
- `chat_id` (string): The unique chat ID for maintaining conversation context.

#### Response

- `response` (string): The assistant's response.
- `action_result` (optional, dict): The result of any executed Neon API call.

## License

This project is licensed under the MIT License.

## Author

[Your Name/Organization]

## Version

0.1.0
