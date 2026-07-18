# Contributing to tracellm-faultline

Thank you for your interest in contributing.

## Getting started

```bash
git clone https://github.com/cybr-wisp/tracellm-faultline.git
cd tracellm-faultline
uv sync --all-extras
```

## Development workflow

1. Create a feature branch from `main`.
2. Write tests for new functionality.
3. Run quality checks before pushing:
   ```bash
   uv run pytest
   uv run mypy src
   uv run ruff check .
   uv run ruff format --check .
   ```
4. Open a pull request with a clear description.

## Code style

- Python 3.11+, strict mypy typing
- Ruff for linting and formatting (line length 100)
- Pydantic for all data schemas
- Async-first for I/O operations

## What not to include

- API keys, credentials, or secrets of any kind
- Proprietary or confidential data from any employer
- Dependencies on platform-specific evaluation services
