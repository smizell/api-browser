from typing import Optional

__all__ = ['is_ref', 'get_with_refs', 'get_schema_name']

def is_ref(value) -> bool:
    """Check if a value is a reference object (has $ref property)."""
    return isinstance(value, dict) and "$ref" in value


def get_schema_name(schema_ref: Optional[str]) -> str:
    """Extract schema name from $ref or return appropriate placeholder."""
    if not schema_ref:
        return "(none)"
    if not schema_ref.startswith("#/components/schemas/"):
        return "(inline)"
    return schema_ref.split("/")[-1]


def get_with_refs(value, path_parts, root=None, default=None):
    """
    Get a value from a nested structure, following any $ref references.
    
    Args:
        value: The value to traverse
        path_parts: List of strings/integers representing the path to follow
        root: The root document for resolving refs (defaults to value if not provided)
        default: Value to return if path is not found (defaults to None)
    
    Returns:
        The value at the path, dereferenced if it's a ref, or default if not found
    """
    if root is None:
        root = value
        
    if not path_parts:
        # If we hit a ref, resolve it and return the dereferenced value
        if is_ref(value):
            ref_path = value["$ref"].lstrip("#/").split("/")
            return get_with_refs(root, ref_path, root, default)
        return value
        
    current_key = path_parts[0]
    remaining_path = path_parts[1:]
    
    # Handle array indexing
    if isinstance(value, list):
        try:
            if not isinstance(current_key, int):
                current_key = int(current_key)
            next_value = value[current_key]
            return get_with_refs(next_value, remaining_path, root, default)
        except (ValueError, IndexError):
            return default
            
    # Handle dict access
    if isinstance(value, dict):
        # If we hit a ref, resolve it first then continue with the path
        if is_ref(value):
            ref_path = value["$ref"].lstrip("#/").split("/")
            resolved_value = get_with_refs(root, ref_path, root, default)
            return get_with_refs(resolved_value, path_parts, root, default)
            
        next_value = value.get(current_key)
        if next_value is None:
            return default
        return get_with_refs(next_value, remaining_path, root, default)
        
    return default 