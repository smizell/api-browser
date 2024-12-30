import pytest
from api_browser import cli  # Update import to only what's needed for this test file
from click.testing import CliRunner
from api_browser import summary, schema, urls, validate_cmd  # Add urls and validate_cmd to imports
import yaml
import tempfile
import os
from pathlib import Path

# Any remaining tests for api_browser functionality would go here

def test_summary_command(snapshot):
    # Create a sample OpenAPI spec
    openapi_spec = {
        "info": {
            "title": "Test API",
            "description": "A test API description"
        },
        "paths": {
            "/pets": {
                "get": {
                    "operationId": "listPets",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PetList"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Create a temporary file with the OpenAPI spec
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(openapi_spec, f)
        temp_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(summary, [temp_file])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)

def test_schema_command(snapshot):
    # Create a sample OpenAPI spec with nested schemas and circular references
    openapi_spec = {
        "paths": {
            "/users": {
                "post": {
                    "operationId": "createUser",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                },
                "get": {
                    "operationId": "listUsers",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/users/{id}": {
                "put": {
                    "operationId": "updateUser",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Pet": {
                    "allOf": [
                        {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "integer"}
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "owner": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    ]
                },
                "Error": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "code": {"type": "integer"},
                                "message": {"type": "string"}
                            }
                        },
                        {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "details": {"type": "string"}
                            }
                        }
                    ]
                },
                "Address": {
                    "type": "object",
                    "required": ["street"],
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {"type": "string"},
                        "user": {"$ref": "#/components/schemas/User"}  # Circular reference
                    }
                },
                "User": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "address": {"$ref": "#/components/schemas/Address"},
                        "pets": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Pet"}
                        },
                        "metadata": {
                            "anyOf": [
                                {"type": "string"},
                                {
                                    "type": "object",
                                    "properties": {
                                        "key": {"type": "string"},
                                        "value": {"type": "string"}
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
    
    # Create a temporary file with the OpenAPI spec
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(openapi_spec, f)
        temp_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(schema, [temp_file, "User"])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)

def test_urls_command(snapshot):
    # Create a sample OpenAPI spec with various URL patterns
    openapi_spec = {
        "paths": {
            "/customers": {
                "get": {"operationId": "listCustomers"},
                "post": {"operationId": "createCustomer"}
            },
            "/customers/{id}": {
                "get": {"operationId": "getCustomer"},
                "put": {"operationId": "updateCustomer"},
                "delete": {"operationId": "deleteCustomer"}
            },
            "/customers/search": {
                "post": {"operationId": "searchCustomers"}
            },
            "/customers/{id}/orders": {
                "get": {"operationId": "listCustomerOrders"},
                "post": {"operationId": "createCustomerOrder"}
            },
            "/customers/{id}/orders/{orderId}": {
                "get": {"operationId": "getCustomerOrder"},
                "put": {"operationId": "updateCustomerOrder"},
                "delete": {"operationId": "deleteCustomerOrder"}
            },
            "/orders": {
                "get": {"operationId": "listOrders"},
                "post": {"operationId": "createOrder"}
            },
            "/orders/{id}": {
                "get": {"operationId": "getOrder"},
                "put": {"operationId": "updateOrder"},
                "delete": {"operationId": "deleteOrder"}
            }
        }
    }
    
    # Create a temporary file with the OpenAPI spec
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(openapi_spec, f)
        temp_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(urls, [temp_file])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)

def test_validate_command_valid(snapshot):
    # Create a valid OpenAPI spec
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {}
    }
    
    # Create a temporary file with the OpenAPI spec
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(openapi_spec, f)
        temp_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(validate_cmd, [temp_file])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        assert result.output.strip() == "✓ OpenAPI specification is valid"
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)

def test_validate_command_invalid(snapshot):
    # Create an invalid OpenAPI spec (missing required fields)
    openapi_spec = {
        "info": {
            "title": "Test API"
            # Missing required version field and openapi version
        },
        "paths": {}
    }
    
    # Create a temporary file with the OpenAPI spec
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(openapi_spec, f)
        temp_file = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(validate_cmd, [temp_file], mix_stderr=True)
        
        # Check that the command failed
        assert result.exit_code == 1
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)
