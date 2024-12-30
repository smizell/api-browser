import pytest
from api_browser.openapi import is_ref, get_with_refs

def test_is_ref():
    assert is_ref({"$ref": "#/components/schemas/Todo"}) == True
    assert is_ref({"foo": "bar"}) == False
    assert is_ref(None) == False
    assert is_ref([]) == False
    assert is_ref("not a ref") == False

def test_get_with_refs_basic_dict():
    data = {
        "foo": {
            "bar": "baz"
        }
    }
    assert get_with_refs(data, ["foo", "bar"]) == "baz"
    assert get_with_refs(data, ["foo"]) == {"bar": "baz"}
    assert get_with_refs(data, ["nonexistent"]) is None
    assert get_with_refs(data, ["foo", "nonexistent"]) is None

def test_get_with_refs_array():
    data = {
        "items": [
            {"name": "first"},
            {"name": "second"}
        ]
    }
    assert get_with_refs(data, ["items", 0, "name"]) == "first"
    assert get_with_refs(data, ["items", 1, "name"]) == "second"
    assert get_with_refs(data, ["items", 2, "name"]) is None
    assert get_with_refs(data, ["items", "not_an_index"]) is None

def test_get_with_refs_with_references():
    data = {
        "components": {
            "schemas": {
                "Todo": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"}
                    }
                }
            }
        },
        "paths": {
            "/todos": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Todo"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Test resolving a reference
    schema_ref = get_with_refs(data, ["paths", "/todos", "get", "responses", "200", 
                                     "content", "application/json", "schema"])
    assert schema_ref == {
        "type": "object",
        "properties": {
            "id": {"type": "integer"}
        }
    }

def test_get_with_refs_nested_references():
    data = {
        "components": {
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"}
                    }
                },
                "TodoResponse": {
                    "$ref": "#/components/schemas/Error"
                }
            }
        }
    }
    
    result = get_with_refs(data, ["components", "schemas", "TodoResponse"])
    assert result == {
        "type": "object",
        "properties": {
            "code": {"type": "integer"}
        }
    }

def test_get_with_refs_empty_path():
    data = {"foo": "bar"}
    assert get_with_refs(data, []) == data

def test_get_with_refs_none_value():
    assert get_with_refs(None, ["any", "path"]) is None

def test_get_with_refs_with_default():
    data = {
        "foo": {
            "bar": "baz"
        }
    }
    # Test with missing path and default value
    assert get_with_refs(data, ["missing"], default="not found") == "not found"
    assert get_with_refs(data, ["foo", "missing"], default={}) == {}
    assert get_with_refs(data, ["foo", "bar", "missing"], default=42) == 42
    
    # Test with existing path (default should be ignored)
    assert get_with_refs(data, ["foo", "bar"], default="ignored") == "baz"
    
    # Test with array index out of bounds
    data_with_array = {"items": [1, 2, 3]}
    assert get_with_refs(data_with_array, ["items", 5], default="out of bounds") == "out of bounds"
    
    # Test with None as default value
    assert get_with_refs(data, ["missing"], default=None) is None
    
    # Test with ref that doesn't exist
    data_with_ref = {
        "broken_ref": {
            "$ref": "#/components/schemas/DoesNotExist"
        }
    }
    assert get_with_refs(data_with_ref, ["broken_ref"], default="ref not found") == "ref not found" 