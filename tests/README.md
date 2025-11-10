# Test Suite Overview

The `tests` directory centralizes automated verification assets.  The initial
focus is on structural validation of Node-RED flows and a framework for future
regression scenarios.

- `schemas/`: JSON schema definitions and related metadata.
- `validate_flows.py`: Lightweight validator that enforces schema constraints
  and basic wiring correctness for production flows under `src/flows`.
- `regression/`: Placeholder fixtures and documentation for future flow
  regression suites.

Run the validator locally with:

```bash
python -m tests.validate_flows
```
