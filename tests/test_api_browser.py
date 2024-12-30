import pytest
from api_browser import cli  # Update import to only what's needed for this test file
from click.testing import CliRunner
from api_browser import summary, schema
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
        "components": {
            "schemas": {
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
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "friends": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "hobbies": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": ["name"],
                                            "properties": {
                                                "name": {"type": "string"},
                                                "level": {"type": "string"}
                                            }
                                        }
                                    }
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
        result = runner.invoke(schema, [temp_file, "User"])
        
        # Check that the command succeeded
        assert result.exit_code == 0
        
        # Compare with snapshot
        assert result.output == snapshot
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)
