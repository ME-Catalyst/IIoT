# Logs and Diagnostics

## Structured Logs

* **Location**: `${LOG_DIRECTORY}` (default `E:\\NodeRed\\Logs`).
* **Files**:
  * `01_GET_*.json` – Raw HTTP responses from the gateway event poll.
  * `MQTT_raw_*.json` – MQTT frames captured from wildcard subscriptions.
  * `MQTT_discard_*.json` – Frames dropped by validation logic.
* Rotate the directory weekly or when files exceed 250 MB.

## Node-RED Logs

* Access system logs via `journalctl -u nodered -f` (Linux) or the Windows Event Viewer when running as a service.
* Enable trace logging temporarily by setting the environment variable `NODE_RED_ENABLE_SAFE_MODE=false` to allow flow redeploys a
fter failures.

## Diagnostics Workflow

1. Export the current flow for backup.
2. Trigger the **Log Reset** inject to capture a clean set of events.
3. Reproduce the issue while the debug sidebar is open in Node-RED.
4. Collect structured logs and Node-RED runtime logs for analysis.
5. Compare the latest flow JSON against the prior release with `npx --yes json-diff` to spot unintended changes.

## Additional Tools

* `python -m tests.validate_flows` – Confirms flow JSON adheres to schema expectations.
* `npx --yes ajv-cli validate` – Validates configuration dictionaries against JSON Schemas.
* `jq` – Pretty-prints MQTT frames and HTTP responses stored in the structured log directory.
