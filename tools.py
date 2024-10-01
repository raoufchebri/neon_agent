tools = [
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Creates a Neon project.\nA project is the top-level object in the Neon object hierarchy.\nPlan limits define how many projects you can create.\nNeon's Free plan permits one project per Neon account.\nFor more information, see [Manage projects](https://neon.tech/docs/manage/projects/).\n\nYou can specify a region and Postgres version in the request body.\nNeon currently supports PostgreSQL 14, 15 and 16. version 17 is coming soon.\nFor supported regions and `region_id` values, see [Regions](https://neon.tech/docs/introduction/regions/).\n",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name.",
                    },
                    "region_id": {
                        "type": "string",
                        "description": "Region ID.",
                        "enum": ["aws-us-east-1", "aws-us-east-2", "aws-us-west-1", "aws-eu-central-1", "aws-ap-southeast-1", "aws-ap-southeast-2"]
                    },
                    "pg_version": {
                        "type": "string",
                        "description": "Postgres version.",
                        "enum": ["14", "15", "16", "17"]
                    },
                    "autoscaling_limit_min_cu": {
                        "type": "integer",
                        "description": "Minimum number of compute units.",
                    },
                    "autoscaling_limit_max_cu": {
                        "type": "integer",
                        "description": "Maximum number of compute units.",
                    }
                },
                "required": [],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_project",
            "description": "Deletes the specified project.\nYou can obtain a `project_id` by listing the projects for your Neon account.\nDeleting a project is a permanent action.\nDeleting a project also deletes endpoints, branches, databases, and users that belong to the project.\n",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The ID of the project to be deleted.",
                    }
                },
                "required": ["project_id"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "strict": True,
            "description": "Retrieves a list of projects for the Neon account.\nA project is the top-level object in the Neon object hierarchy.\nFor more information, see [Manage projects](https://neon.tech/docs/manage/projects/).\n",
            "parameters": {
                "type": "object",
                "properties": {
                },
                "required": [],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project",
            "strict": True,
            "description": "Retrieves information about the specified project.\nA project is the top-level object in the Neon object hierarchy.\nYou can obtain a `project_id` by listing the projects for your Neon account.\n",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_connection_uri",
            "description": "Retrieves a connection URI for the specified database.\nYou can obtain a `project_id` by listing the projects for your Neon account.\nYou can obtain the `database_name` by listing the databases for a branch.\nYou can obtain a `role_name` by listing the roles for a branch.\n",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The Neon project ID",
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "The branch ID. Defaults to your project's default `branch_id` if not specified.",
                    },
                    "endpoint_id": {
                        "type": "string",
                        "description": "The endpoint ID. Defaults to the read-write `endpoint_id` associated with the `branch_id` if not specified.",
                    },
                    "database_name": {
                        "type": "string",
                        "description": "The database name",
                    },
                    "role_name": {
                        "type": "string",
                        "description": "The role name",
                    },
                    "pooled": {
                        "type": "boolean",
                        "description": "Adds the `-pooler` option to the connection URI when set to `true`, creating a pooled connection URI.",
                    },
                },
                "required": ["project_id", "database_name", "role_name"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_project_branch",
            # "strict": True,
            "description": "Creates a branch in the specified project.\nYou can obtain a `project_id` by listing the projects for your Neon account.\n\nThis method does not require a request body, but you can specify one to create a compute endpoint for the branch or to select a non-default parent branch.\nThe default behavior is to create a branch from the project's default branch with no compute endpoint, and the branch name is auto-generated.\nThere is a maximum of one read-write endpoint per branch.\nA branch can have multiple read-only endpoints.\nFor related information, see [Manage branches](https://neon.tech/docs/manage/branches/).\n",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The Neon project ID",
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "The parent branch ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "The branch name",
                    },
                    "endpoint_type": {
                        "type": "string",
                        "description": "The endpoint type",
                        "enum": ["read-write", "read-only"],
                    },
                },
                "required": ["project_id"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_project_branches",
            "description": "Retrieves a list of branches for the specified project.\nYou can obtain a `project_id` by listing the projects for your Neon account.\n\nEach Neon project has a root branch named `main`.\nA `branch_id` value has a `br-` prefix.\nA project may contain child branches that were branched from `main` or from another branch.\nA parent branch is identified by the `parent_id` value, which is the `id` of the parent branch.\nFor related information, see [Manage branches](https://neon.tech/docs/manage/branches/).\n",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }   
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_branch",
            "description": "Retrieves information about the specified branch.\nYou can obtain a `project_id` by listing the projects for your Neon account.\nYou can obtain a `branch_id` by listing the branches for a project.\n",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_project_branch",
            "strict": True,
            "description": "Deletes the specified branch.\nYou can obtain a `project_id` by listing the projects for your Neon account.\nYou can obtain a `branch_id` by listing the branches for a project.\n",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,          
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_project_branch",
            "description": "Updates the specified branch.\nYou can obtain a `project_id` by listing the projects for your Neon account.\nYou can obtain a `branch_id` by listing the branches for a project.\n",    
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
    }
    
]