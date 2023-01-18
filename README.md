# Description
Python Command Line Tools for interacting with Multivers<sup>X</sup>.

## Documentation
[docs.multiversx.com](https://docs.multiversx.com/sdk-and-tools/sdk-py/)

## CLI
[CLI](CLI.md)

## Distribution
[mxpy-up](https://docs.multiversx.com/sdk-and-tools/sdk-py/installing-mxpy/) and [PyPi](https://pypi.org/project/multiversx-sdk-cli/#history)

## Development setup

### Virtual environment

Create a virtual environment and install the dependencies:

```
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r ./requirements.txt --upgrade
```

Install development dependencies, as well:

```
pip install -r ./requirements-dev.txt --upgrade
```

Above, `requirements.txt` should mirror the **dependencies** section of `setup.py`.

If using VSCode, restart it or follow these steps:
 - `Ctrl + Shift + P`
 - _Select Interpreter_
 - Choose `./.venv/bin/python`.
