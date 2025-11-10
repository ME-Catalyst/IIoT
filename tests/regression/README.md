# Flow Regression Scaffolding

This directory hosts placeholder assets for future regression suites.
The intent is to capture golden Node-RED exports or representative payloads
that can be replayed to validate changes to the production flows located in
`src/flows/production`.

Add new fixtures under subfolders named for the subsystem under test, then
extend `tests/validate_flows.py` or accompanying scripts to replay the assets
and compare the resulting outputs.
