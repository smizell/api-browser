import click
import flask.cli
import logging
import os
import webbrowser
from flask import Flask, render_template
from threading import Timer
from tabulate import tabulate
from typing import Optional
import yaml  # Import at function level to avoid global import

####### Server

current_dir = os.path.dirname(__file__)
template_dir = os.path.abspath(os.path.join(current_dir, "templates"))

app = Flask(__name__, template_folder=template_dir)

# Flask shows some stuff during boot I don't want to show
# This disables that. We'll improve this later by maybe
# moving to a different HTTP app.
log = logging.getLogger("werkzeug")
log.disabled = True
flask.cli.show_server_banner = lambda *args: None


@app.route("/openapi")
def read_openapi():
    with open(app.config["OPENAPI_FILENAME"]) as f:
        content = f.read()
    return content


@app.route("/openapi-documentation")
def openapi_documentation():
    return render_template("redoc.html")


####### CLI


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename")
def openapi(filename):
    click.echo("Running API Browser server at 127.0.0.1:5000")
    click.echo("Press Ctrl+c to stop the server")
    app.config["OPENAPI_FILENAME"] = filename
    # We use a Timer so we can wait on the server to start since it blocks the thread
    Timer(0.5, _open_browser).start()
    app.run(host="127.0.0.1", port="5000", debug=False, use_reloader=False)


def _open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/openapi-documentation")


def get_schema_name(schema_ref: Optional[str]) -> str:
    """Extract schema name from $ref or return appropriate placeholder."""
    if not schema_ref:
        return "(none)"
    if not schema_ref.startswith("#/components/schemas/"):
        return "(inline)"
    return schema_ref.split("/")[-1]


def get_response_schema_name(responses: dict) -> str:
    """Get schema name for success response (2xx)."""
    for status_code, response in responses.items():
        if 200 <= int(status_code) <= 299:
            content = get_with_refs(response, ["content"], default={})
            if not content:
                return "(none)"
            
            # Get the first content type (usually application/json)
            first_content = next(iter(content.values()))
            schema = get_with_refs(first_content, ["schema"], default={})
            ref = get_with_refs(schema, ["$ref"], default=None)
            return get_schema_name(ref)
    return "(none)"


def get_request_schema_name(operation: dict) -> str:
    """Get schema name for request body."""
    request_body = get_with_refs(operation, ["requestBody"], default={})
    if not request_body:
        return "(none)"
    
    content = get_with_refs(request_body, ["content"], default={})
    if not content:
        return "(none)"
    
    # Get the first content type (usually application/json)
    first_content = next(iter(content.values()))
    schema = get_with_refs(first_content, ["schema"], default={})
    ref = get_with_refs(schema, ["$ref"], default=None)
    return get_schema_name(ref)


def get_success_status_code(responses: dict) -> str:
    """Get the first success status code (2xx) from responses."""
    for status_code, response in responses.items():
        if 200 <= int(status_code) <= 299:
            return str(status_code)
    return "-"


@click.command()
@click.argument("filename")
def summary(filename):
    """Display a summary table of all API endpoints."""
    # Read and parse the OpenAPI file
    with open(filename) as f:
        api_spec = yaml.safe_load(f)
    
    # Print title and description if available
    info = get_with_refs(api_spec, ["info"], default={})
    title = get_with_refs(info, ["title"], default="Untitled API")
    description = get_with_refs(info, ["description"], default="No description provided")
    
    click.echo(f"Title: {title}")
    click.echo(f"Description: {description}")
    click.echo()  # Add blank line before table
    
    rows = []
    
    paths = get_with_refs(api_spec, ["paths"], default={})
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method == "parameters":  # Skip common parameters
                continue
                
            operation_id = get_with_refs(operation, ["operationId"], default="")
            request_schema = get_request_schema_name(operation)
            responses = get_with_refs(operation, ["responses"], default={})
            response_schema = get_response_schema_name(responses)
            status_code = get_success_status_code(responses)
            
            rows.append([
                path,
                method.upper(),
                operation_id,
                status_code,
                request_schema,
                response_schema
            ])
    
    # Sort rows by path (first column)
    rows.sort(key=lambda x: x[0])
    
    headers = ["Path", "Method", "Operation ID", "Status", "Request Schema", "Response Schema"]
    click.echo(tabulate(rows, headers=headers, tablefmt="grid"))


# Add the new command to the CLI group
cli.add_command(summary)


def is_ref(value) -> bool:
    """Check if a value is a reference object (has $ref property)."""
    return isinstance(value, dict) and "$ref" in value


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


if __name__ == "__main__":
    cli()
