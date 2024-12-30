# api-browser

[![PyPI](https://img.shields.io/pypi/v/api-browser.svg)](https://pypi.org/project/api-browser/)
[![Tests](https://github.com/smizell/api-browser/actions/workflows/test.yml/badge.svg)](https://github.com/smizell/api-browser/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/smizell/api-browser?include_prereleases&label=changelog)](https://github.com/smizell/api-browser/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/smizell/api-browser/blob/main/LICENSE)

Browse and analyze OpenAPI documentation from your terminal.

## Installation

Install with `pipx` (recommended):

* [Install pipx](https://pipx.pypa.io/latest/installation/)
* Run `pipx install api-browser`

Or install with `pip`:

```bash
pip install api-browser
```

## Commands

### `api_browser openapi <filename>`

Start a local server to view the OpenAPI documentation in a web browser using Redoc. The page will automatically refresh when the OpenAPI file changes.

### `api_browser summary <filename>`

Display a summary table of all API endpoints in the terminal, showing:
- Path
- HTTP Method
- Operation ID
- Status Code
- Request Schema
- Response Schema

Example output:
```
Title: Test API
Description: A test API description

+--------+----------+----------------+----------+------------------+-------------------+
| Path   | Method   | Operation ID   |   Status | Request Schema   | Response Schema   |
+========+==========+================+==========+==================+===================+
| /pets  | GET      | listPets       |      200 | (none)           | PetList           |
+--------+----------+----------------+----------+------------------+-------------------+
```

### `api_browser schema <filename> <schema_name>`

Display a schema from the OpenAPI file in a tree format. Shows:
- Property names (required properties marked with *)
- Property types and references
- Nested object structures
- Array types
- Where the schema is used (requests, responses, and other schemas)

Example output:
```
Schema: User
Referenced by: Address, Pet
Requests: createUser, updateUser
Responses: getUser, listUsers

├── id* (integer)
├── name* (string)
├── email (string)
├── address (Address)
│   ├── street* (string)
│   ├── city (string)
│   └── country (string)
└── pets (array[Pet])
    ├── name* (string)
    └── age (integer)
```

### `api_browser urls <filename>`

Display a tree view of URL segments, showing the API's hierarchical structure and available operations at each endpoint.

Example output:
```
├── customers (createCustomer, listCustomers)
│   ├── search (searchCustomers)
│   └── {id} (deleteCustomer, getCustomer, updateCustomer)
│       └── orders (createCustomerOrder, listCustomerOrders)
│           └── {orderId} (deleteCustomerOrder, getCustomerOrder, updateCustomerOrder)
└── orders (createOrder, listOrders)
    └── {id} (deleteOrder, getOrder, updateOrder)
```

### `api_browser validate <filename>`

Validate an OpenAPI file against the OpenAPI 3.0 specification. Shows a checkmark (✓) if valid or outputs validation errors if there are issues.

Example of valid file:
```
✓ OpenAPI specification is valid
```

Example of invalid file:
```
'title' is a required property

Failed validating 'required' in schema['properties']['info']:
    {'$comment': 'https://spec.openapis.org/oas/v3.1.0#info-object',
     'type': 'object',
     'properties': {'title': {'type': 'string'},
                   'summary': {'type': 'string'},
                   'description': {'type': 'string'},
                   'termsOfService': {'type': 'string', 'format': 'uri'},
                   'contact': {'$ref': '#/$defs/contact'},
                   'license': {'$ref': '#/$defs/license'},
                   'version': {'type': 'string'}},
     'required': ['title', 'version'],
     '$ref': '#/$defs/specification-extensions',
     'unevaluatedProperties': False}

On instance['info']:
    {}
```

## Development

To contribute to api-browser:

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[test]"
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Update snapshots when output changes:
   ```bash
   pytest --snapshot-update
   ```
   Or update specific test snapshots:
   ```bash
   pytest -k "test_name" --snapshot-update
   ```
