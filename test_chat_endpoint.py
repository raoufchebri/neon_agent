import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app  # Replace 'main' with the actual module name if different
import neon_api_utils

# Load environment variables from .env file
load_dotenv()

client = TestClient(app)

# Get Neon API key from .env file
NEON_API_KEY = os.getenv("NEON_API_KEY")

@pytest.fixture
def mock_neon_api_client(monkeypatch):
    def mock_execute_api_call(function_name, neon_api_key, **kwargs):
        if function_name == "create_branch":
            return {"status": "success", "branch_id": "new-branch-id"}
        elif function_name == "list_projects":
            return {
                "projects": [
                    {"id": "project1", "name": "Project 1"},
                    {"id": "project2", "name": "Project 2"}
                ]
            }
        return {"status": "unknown function"}

    monkeypatch.setattr("neon_api_utils.execute_api_call", mock_execute_api_call)

def test_chat_endpoint(mock_neon_api_client):
    # Update the URL to the correct endpoint
    response = client.post("/chat", json={"query": "Hello, how are you?", "neon_api_key": NEON_API_KEY})
    
    # Debugging: Print response content for more details
    print(response.json())
    
    assert response.status_code == 200  # Expecting 200 OK

def test_list_projects_via_chat(mock_neon_api_client):
    # Prompt the AI to list all projects
    response = client.post("/chat", json={"query": "List all my projects", "neon_api_key": NEON_API_KEY})
    
    # Debugging: Print response content for more details
    print(response.json())
    
    assert response.status_code == 200  # Expecting 200 OK
    response_data = response.json()
    
    # Check if the response contains the expected list of projects
    assert "projects" in response_data["action_result"]  # Adjusted to check within "action_result"
    projects = response_data["action_result"]["projects"]
    
    # Additional checks can be added here if needed
