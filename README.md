# api-browser

[![PyPI](https://img.shields.io/pypi/v/api-browser.svg)](https://pypi.org/project/api-browser/)
[![Tests](https://github.com/smizell/api-browser/actions/workflows/test.yml/badge.svg)](https://github.com/smizell/api-browser/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/smizell/api-browser?include_prereleases&label=changelog)](https://github.com/smizell/api-browser/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/smizell/api-browser/blob/main/LICENSE)

Browse API documentation

## Installation

You can use `pipx` to install this tool.

* [Install pipx](https://pipx.pypa.io/latest/installation/)
* Run `pipx install api-browser`

You can also use `pip`:

```bash
pip install api-browser
```
## Usage

See `api_browser --help` for all details.

### `api_browser openapi <filename>`

Load the OpenAPI file and show Redoc documentation. Refresh the page to load any changes to the OpenAPI file.

### `api_browser summary <filename>`

Display a summary table of the API endpoints in the terminal.

### `api_browser schema <filename> <schema_name>`

Display a schema from the OpenAPI file in a concise tree format. Required properties are marked with an asterisk (*).

### `api_browser urls <filename>`

Display a tree view of URL segments from the OpenAPI file, showing how endpoints are hierarchically organized. Each endpoint shows its available operation IDs.

Example:
```
├── customers (listCustomers, createCustomer)
│   ├── {id} (getCustomer, updateCustomer, deleteCustomer)
│   │   └── orders (listCustomerOrders, createCustomerOrder)
│   │       └── {orderId} (getCustomerOrder, updateCustomerOrder, deleteCustomerOrder)
│   └── search (searchCustomers)
└── orders (listOrders, createOrder)
    └── {id} (getOrder, updateOrder, deleteOrder)
```

This visualization helps understand the API's URL structure, how different endpoints are related, and what operations are available at each endpoint.

### `api_browser validate <filename>`

Validate an OpenAPI file against the OpenAPI 3.0 specification. Shows a checkmark (✓) if valid or an error message (✗) with details if there are validation issues.

Example of valid file:
```
✓ OpenAPI specification is valid
```

Example of invalid file:
```
✗ Error: 'openapi' is a required property
```

## Development

### Installation

Clone the repository and install the package in development mode with test dependencies:

```bash
pip install -e ".[test]"
```

### Running Tests

Run all tests:
```bash
pytest
```

Update snapshots when output changes:
```bash
pytest --snapshot-update
```

Update specific test snapshots:
```bash
pytest -k "test_name" --snapshot-update
```

### Commands

#### `api-browser openapi <filename>`

Start a local server to view the OpenAPI documentation in a web browser.

#### `api-browser summary <filename>`

Display a summary table of all API endpoints, including:
- Path
- HTTP Method
- Operation ID
- Status Code
- Request Schema
- Response Schema

#### `api-browser schema <filename> <schema_name>`

Display a schema from the OpenAPI file in a tree format. Required properties are marked with an asterisk (*).

Example:
```
Schema: User
* indicates required property

├── id* (integer)
├── name* (string)
├── email (string)
└── address (Address)
    ├── street* (string)
    ├── city (string)
    └── country (string)
```
