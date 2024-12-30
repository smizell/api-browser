import click
import flask.cli
import logging
import os
import webbrowser
import yaml
from flask import Flask, render_template
from threading import Timer
from tabulate import tabulate
from typing import Optional
from .openapi import is_ref, get_with_refs, get_schema_name

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


def get_response_schema_name(responses: dict) -> str:
    """Get schema name for success response (2xx)."""
    for status_code, response in responses.items():
        if 200 <= int(status_code) <= 299:
            content = get_with_refs(response, ["content"], default={})
            if not content:
                return "(none)"
            
            # Get the first content type (usually application/json)
            first_content = next(iter(content.values()))
            schema = first_content.get("schema", {})
            
            # Check if it's a reference before resolving
            if is_ref(schema):
                return get_schema_name(schema["$ref"])
            return "(inline)"
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
    schema = first_content.get("schema", {})
    
    # Check if it's a reference before resolving
    if is_ref(schema):
        return get_schema_name(schema["$ref"])
    return "(inline)"


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


@click.command()
@click.argument("filename")
@click.argument("schema_name")
def schema(filename, schema_name):
    """Display a schema from the OpenAPI file in a tree format."""
    # Read and parse the OpenAPI file
    with open(filename) as f:
        api_spec = yaml.safe_load(f)
    
    def get_schema_by_ref(ref: str):
        """Get a schema by its reference."""
        if not ref.startswith("#/"):
            return None
        parts = ref.lstrip("#/").split("/")
        current = api_spec
        for part in parts:
            if part not in current:
                return None
            current = current[part]
        return current
    
    def print_schema_tree(schema: dict, indent: str = "", schema_ref: str = None, ref_path: list = None):
        """Print a schema as a tree."""
        if not isinstance(schema, dict):
            return
            
        if ref_path is None:
            ref_path = []
            
        # Handle circular references
        if schema_ref and schema_ref in ref_path:
            click.echo(f"{indent}[Circular reference to {schema_ref}]")
            return
            
        # Add current ref to path
        current_path = ref_path + ([schema_ref] if schema_ref else [])
            
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for i, (prop_name, prop_schema) in enumerate(properties.items()):
            is_last = i == len(properties) - 1
            prefix = "└── " if is_last else "├── "
            next_indent = indent + ("    " if is_last else "│   ")
            indicator = "*" if prop_name in required else ""
            
            if is_ref(prop_schema):
                ref = prop_schema["$ref"]
                ref_name = ref.split("/")[-1]
                click.echo(f"{indent}{prefix}{prop_name}{indicator} ({ref_name})")
                
                # Only expand if not creating a cycle
                if ref not in current_path:
                    ref_schema = get_schema_by_ref(ref)
                    if ref_schema:
                        print_schema_tree(ref_schema, next_indent, ref, current_path)
            else:
                prop_type = prop_schema.get("type", "object")
                
                if prop_type == "array":
                    items = prop_schema.get("items", {})
                    if is_ref(items):
                        ref_name = items["$ref"].split("/")[-1]
                        click.echo(f"{indent}{prefix}{prop_name}{indicator} (array[{ref_name}])")
                        
                        if items["$ref"] not in current_path:
                            ref_schema = get_schema_by_ref(items["$ref"])
                            if ref_schema:
                                print_schema_tree(ref_schema, next_indent, items["$ref"], current_path)
                    else:
                        item_type = items.get("type", "object")
                        if item_type in ["string", "number", "integer", "boolean"]:
                            click.echo(f"{indent}{prefix}{prop_name}{indicator} (array[{item_type}])")
                        else:
                            click.echo(f"{indent}{prefix}{prop_name}{indicator} (array[object])")
                            print_schema_tree(items, next_indent, None, current_path)
                elif prop_type in ["string", "number", "integer", "boolean"]:
                    click.echo(f"{indent}{prefix}{prop_name}{indicator} ({prop_type})")
                else:
                    click.echo(f"{indent}{prefix}{prop_name}{indicator} (object)")
                    print_schema_tree(prop_schema, next_indent, None, current_path)
    
    # Get the initial schema
    schema_data = api_spec.get("components", {}).get("schemas", {}).get(schema_name)
    if schema_data is None:
        click.echo(f"Schema '{schema_name}' not found", err=True)
        return
    
    # Print the schema tree
    click.echo(f"Schema: {schema_name}")
    click.echo("* indicates required property")
    click.echo()
    print_schema_tree(schema_data)


# Add the new command to the CLI group
cli.add_command(summary)
cli.add_command(schema)


if __name__ == "__main__":
    cli()
