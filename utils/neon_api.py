"""
Neon API Specifications

This module provides a set of functions to interact with the Neon API.
It includes operations for managing projects, branches, and retrieving connection URIs.

The module uses environment variables for API key management and implements
error handling and response processing for API calls.

Dependencies:
- requests: For making HTTP requests to the Neon API
- os: For environment variable handling
- dotenv: For loading environment variables from a .env file

Usage:
Ensure you have set up your Neon API key in your environment variables or .env file.
Then, you can import and use the functions provided in this module to interact with your Neon projects.

Author: [Your Name/Organization]
License: [Your chosen license, e.g., MIT, Apache 2.0, etc.]
"""

import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the Neon API
BASE_URL = "https://console.neon.tech/api/v2"

# Load environment variables from .env file
load_dotenv()

def execute_api_call(function_name, neon_api_key, **function_args):
    """
    Execute an API call based on the provided function name.

    Args:
        function_name (str): The name of the API function to call.
        neon_api_key (str): The Neon API key for authentication.
        **function_args: Additional arguments specific to the API function.

    Returns:
        dict: The result of the API call or an error message.
    """
    api_functions = {
        "create_project": create_project,
        "list_projects": list_projects,
        "get_project": get_project,
        "get_connection_uri": get_connection_uri,
        "create_project_branch": create_project_branch,
        "list_project_branches": list_project_branches,
        "get_project_branch": get_project_branch,
        "delete_project_branch": delete_project_branch,
        "update_project_branch": update_project_branch,
        "delete_project": delete_project
    }
    
    if function_name in api_functions:
        return api_functions[function_name](neon_api_key=neon_api_key, **function_args)
    else:
        return {"error": "Unknown function call"}

def handle_response(response):
    """
    Handle the API response, raising exceptions for HTTP errors and returning JSON content.

    Args:
        response (requests.Response): The response object from the API call.

    Returns:
        dict: The JSON content of the response.

    Raises:
        requests.exceptions.HTTPError: If the API call was unsuccessful.
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError: {e}")
        logger.error(f"Response status code: {response.status_code}")
        logger.error(f"Response content: {response.content}")
        raise
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.content}")
    return response.json()

def list_projects(neon_api_key):
    """
    List all projects for the authenticated user.

    Args:
        neon_api_key (str): The Neon API key for authentication.

    Returns:
        dict: A dictionary containing the list of projects.
    """
    url = f"{BASE_URL}/projects"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return handle_response(response)

def get_project(neon_api_key, project_id: str):
    """
    Get details of a specific project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project to retrieve.

    Returns:
        dict: A dictionary containing the project details.
    """
    url = f"{BASE_URL}/projects/{project_id}"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return handle_response(response)

def create_project(neon_api_key, name=None, region_id=None, pg_version=None, autoscaling_limit_min_cu=None, autoscaling_limit_max_cu=None):
    """
    Create a new project with the specified parameters.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        name (str, optional): The name of the project.
        region_id (str, optional): The ID of the region for the project.
        pg_version (str, optional): The PostgreSQL version for the project.
        autoscaling_limit_min_cu (int, optional): The minimum autoscaling limit in compute units.
        autoscaling_limit_max_cu (int, optional): The maximum autoscaling limit in compute units.

    Returns:
        dict: A dictionary containing the details of the created project.
    """
    url = f"{BASE_URL}/projects"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    payload = {"project": {}}
    if name is not None:
        payload["project"]["name"] = name
    if region_id is not None:
        payload["project"]["region_id"] = region_id
    if pg_version is not None:
        payload["project"]["pg_version"] = pg_version
    if autoscaling_limit_min_cu is not None:
        payload["project"]["autoscaling_limit_min_cu"] = autoscaling_limit_min_cu
    if autoscaling_limit_max_cu is not None:
        payload["project"]["autoscaling_limit_max_cu"] = autoscaling_limit_max_cu
    response = requests.post(url, headers=headers, json=payload)
    return handle_response(response)

def delete_project(neon_api_key, project_id):
    """
    Delete a specified project.

    This function deletes the specified project and all its associated resources,
    including endpoints, branches, databases, and users. This action is permanent
    and cannot be undone.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project to be deleted.

    Returns:
        dict: A dictionary containing the response from the API.

    Raises:
        Exception: If there's an error in the API request or response.
    """
    url = f"{BASE_URL}/projects/{project_id}"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.delete(url, headers=headers)
        return handle_response(response)
    except Exception as e:
        print(f"An error occurred while deleting the project: {str(e)}")
        raise


def get_connection_uri(neon_api_key, project_id: str, database_name: str = "neondb", role_name: str = "neondb_owner", branch_id: str = None, endpoint_id: str = None, pooled: bool = None):
    """
    Get the connection URI for a specific database in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.
        database_name (str, optional): The name of the database. Defaults to "neondb".
        role_name (str, optional): The name of the role. Defaults to "neondb_owner".
        branch_id (str, optional): The ID of the branch.
        endpoint_id (str, optional): The ID of the endpoint.
        pooled (bool, optional): Whether to use connection pooling.

    Returns:
        dict: A dictionary containing the connection URI.
    """
    url = f"{BASE_URL}/projects/{project_id}/connection_uri"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "database_name": database_name,
        "role_name": role_name
    }
    if branch_id is not None:
        params["branch_id"] = branch_id
    if endpoint_id is not None:
        params["endpoint_id"] = endpoint_id
    if pooled is not None:
        params["pooled"] = str(pooled).lower()

    try:
        response = requests.get(url, headers=headers, params=params)
        return handle_response(response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def create_project_branch(neon_api_key, project_id, parent_id=None, name=None, endpoint_type=None):
    """
    Create a new branch in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.
        parent_id (str, optional): The ID of the parent branch.
        name (str, optional): The name of the new branch.
        endpoint_type (str, optional): The type of endpoint for the branch.

    Returns:
        dict: A dictionary containing the details of the created branch.
    """
    url = f"{BASE_URL}/projects/{project_id}/branches"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    payload = {"branch": {}}
    if parent_id is not None:
        payload["branch"]["parent_id"] = parent_id
    if name is not None:
        payload["branch"]["name"] = name
    if endpoint_type is not None:
        payload["endpoints"] = [{"type": endpoint_type}]
    
    response = requests.post(url, headers=headers, json=payload)
    return handle_response(response)

def list_project_branches(neon_api_key, project_id):
    """
    List all branches in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.

    Returns:
        dict: A dictionary containing the list of branches.
    """
    url = f"{BASE_URL}/projects/{project_id}/branches"
    headers = {
        "Authorization": f"Bearer {neon_api_key}"
    }
    
    response = requests.get(url, headers=headers)
    return handle_response(response)

def get_project_branch(neon_api_key, project_id, branch_id):
    """
    Get details of a specific branch in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.
        branch_id (str): The ID of the branch.

    Returns:
        dict: A dictionary containing the branch details.
    """
    url = f"{BASE_URL}/projects/{project_id}/branches/{branch_id}"
    headers = {
        "Authorization": f"Bearer {neon_api_key}"
    }
    
    response = requests.get(url, headers=headers)
    return handle_response(response)

def delete_project_branch(neon_api_key, project_id, branch_id):
    """
    Delete a specific branch in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.
        branch_id (str): The ID of the branch to delete.

    Returns:
        dict: A dictionary containing the result of the deletion operation.
    """
    url = f"{BASE_URL}/projects/{project_id}/branches/{branch_id}"
    headers = {
        "Authorization": f"Bearer {neon_api_key}"
    }
    
    response = requests.delete(url, headers=headers)
    return handle_response(response)

def update_project_branch(neon_api_key, project_id, branch_id, name=None):
    """
    Update a specific branch in a project.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        project_id (str): The ID of the project.
        branch_id (str): The ID of the branch to update.
        name (str, optional): The new name for the branch.

    Returns:
        dict: A dictionary containing the updated branch details.
    """
    url = f"{BASE_URL}/projects/{project_id}/branches/{branch_id}"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Content-Type": "application/json"
    }
    payload = {"branch": {}}
    if name is not None:
        payload["branch"]["name"] = name
    
    response = requests.patch(url, headers=headers, json=payload)
    return handle_response(response)
