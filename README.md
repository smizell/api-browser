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

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd api-browser
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```

### Snapshot Testing

The test suite includes snapshot tests that verify the exact output of commands. If you make changes that intentionally modify the output format, you'll need to update the snapshots.

To update snapshots:
```bash
rm tests/snapshots/summary_output.txt
pytest
```

The first test run will create a new snapshot with the current output. Subsequent runs will verify against this new snapshot.
