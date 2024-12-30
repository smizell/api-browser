import pytest
from api_browser import cli  # Update import to only what's needed for this test file
from click.testing import CliRunner
from api_browser import summary
import yaml
import tempfile
import os
from pathlib import Path

# Any remaining tests for api_browser functionality would go here

def test_summary_command():
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
                                    "schema": {
                                        "$ref": "#/components/schemas/PetList"
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "operationId": "createPet",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Pet"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Pet"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/pets/{id}": {
                "get": {
                    "operationId": "getPet",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"}
                                        }
                                    }
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
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                },
                "PetList": {
                    "type": "array",
                    "items": {
                        "$ref": "#/components/schemas/Pet"
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
        
        # Load expected output from snapshot file
        snapshot_path = Path(__file__).parent / "snapshots" / "summary_output.txt"
        if not snapshot_path.exists():
            # Create snapshots directory if it doesn't exist
            snapshot_path.parent.mkdir(exist_ok=True)
            # Create initial snapshot
            snapshot_path.write_text(result.output)
            pytest.skip("Created initial snapshot")
        
        # Compare with snapshot
        expected_output = snapshot_path.read_text()
        assert result.output == expected_output
        
    finally:
        # Clean up the temporary file
        os.unlink(temp_file)
