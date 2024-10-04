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

import json
import requests
import os
from dotenv import load_dotenv
import logging
import psycopg2
from psycopg2 import sql

from config import CHAT_MODEL, FUNCTION_CALL_MODEL, client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for the Neon API
BASE_URL = "https://console.neon.tech/api/v2"

# Load environment variables from .env file
load_dotenv()

def execute_api_call(function_name, neon_api_key, messages=None, **function_args):
    """
    Execute an API call based on the provided function name.

    Args:
        function_name (str): The name of the API function to call.
        neon_api_key (str): The Neon API key for authentication.
        messages (list, optional): List of messages to pass to the function.
        **function_args: Additional arguments specific to the API function.

    Returns:
        dict: The result of the API call or an error message.
    """

    logger.info(f"function_name: {function_name}")
    logger.info(f"function_args: {function_args}")
    
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
        "delete_project": delete_project,
        "execute_sql_query": execute_sql_query,
    }
    
    if function_name in api_functions:
        if function_name == "execute_sql_query":
            return api_functions[function_name](neon_api_key=neon_api_key, messages=messages, **function_args)
        else:
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
        return {"error": f"HTTPError: {e}"}
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
    logger.info(f"project_id: {project_id}")
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

def get_current_user_info(neon_api_key):
    """
    Get current user details from the Neon API.

    This function retrieves information about the current Neon user account,
    including billing details, authentication accounts, and usage limits.

    Args:
        neon_api_key (str): The Neon API key for authentication.

    Returns:
        dict: A dictionary containing the current user's information.
              The 'id' field in this dictionary is the user's unique identifier.

    Raises:
        Exception: If there's an error in the API request or response.
    """
    url = f"{BASE_URL}/users/me"
    headers = {
        "Authorization": f"Bearer {neon_api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        user_info = handle_response(response)
        
        # Extract and return the user ID
        user_id = user_info.get('id')
        if user_id:
            logger.info(f"Successfully retrieved user info. User ID: {user_id}")
        else:
            logger.warning("User ID not found in the response")
        
        return user_id
    except Exception as e:
        logger.error(f"An error occurred while getting user info: {str(e)}")
        raise


def execute_sql_query(neon_api_key, database_url, sql_query, messages=None):
    """
    Execute a SQL query on a PostgreSQL database and return the result.

    Args:
        database_url (str): The connection URL for the PostgreSQL database.
        sql_query (str): The SQL query to execute.
        messages (list, optional): List of messages to pass to the function.

    Returns:
        list: A list of tuples containing the query results, or an empty list for non-SELECT queries.

    Raises:
        Exception: If there's an error connecting to the database or executing the query.
    """

    conn = None
    try:
        conn = psycopg2.connect(database_url, sslmode='require')
        schema = fetch_database_schema(conn=conn)

        tool_call = None
        while True:
            message = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a PostgreSQL AI Assistant. Based on the database schema and user query, generate the correct SQL query'"},
                    {"role": "user", "content": f"Database schema: {schema}"},
                    {"role": "user", "content": f"User query: {sql_query}"},
                    {"role": "user", "content": f"Previously generated SQL query: {sql_query}"}
                ] + (messages if messages else []),
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_query",
                            "strict": True,
                            "description": "Execute a SQL query on a PostgreSQL database and return the result.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "sql_query": {
                                        "type": "string",
                                        "description": "The SQL query to execute.",
                                    }
                                },
                                "required": ["sql_query"],
                                "additionalProperties": False,
                            },
                        }
                    }
                ]
            ).choices[0].message

            if message.tool_calls:
                break
        tool_call = message.tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)
        logger.info({"SQL Query": function_args})
        return execute_query(conn, **function_args)
    except Exception as e:
        logger.error(f"An error occurred in execute_sql_query: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

    

def execute_query(conn, sql_query):
    """
    Execute a SQL query on a PostgreSQL database and return the result.

    Args:
        database_url (str): The connection URL for the PostgreSQL database.
        sql_query (str): The SQL query to execute.

    Returns:
        list: A list of tuples containing the query results, or an empty list for non-SELECT queries.

    Raises:
        Exception: If there's an error connecting to the database or executing the query.
    """

    try:

        cur = conn.cursor()
     
        # Execute the query
        cur.execute(sql.SQL(sql_query))
        
        # If the query is a SELECT statement, fetch the results
        if sql_query.strip().lower().startswith("select"):
            results = cur.fetchall()
        else:
            # Commit the transaction for non-SELECT queries
            conn.commit()
            results = []

        # Close the cursor and connection
        cur.close()
        
        return results
    except Exception as e:
        logger.error(f"An error occurred while executing SQL query: {str(e)}")
        raise


def fetch_database_schema(conn):
    """
    Fetch the schema of the database.

    Args:
        neon_api_key (str): The Neon API key for authentication.
        database_url (str): The connection URL for the PostgreSQL database.

    Returns:
        list: A list of dictionaries containing table names and their column information.

    Raises:
        Exception: If there's an error connecting to the database or executing the query.
    """
    schema_query = """
    SELECT 
        table_name, 
        column_name, 
        data_type, 
        is_nullable
    FROM 
        information_schema.columns
    WHERE 
        table_schema = 'public'
    ORDER BY 
        table_name, ordinal_position;
    """

    try:
        results = execute_query(conn, schema_query)
        
        schema = {}
        for row in results:
            table_name, column_name, data_type, is_nullable = row
            if table_name not in schema:
                schema[table_name] = []
            schema[table_name].append({
                "column_name": column_name,
                "data_type": data_type,
                "is_nullable": is_nullable
            })

        return [{"table_name": table, "columns": columns} for table, columns in schema.items()]
    except Exception as e:
        logger.error(f"An error occurred while fetching database schema: {str(e)}")
        raise
