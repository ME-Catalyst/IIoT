# Industrial IoT Data Pipeline

This repository contains a production-ready Node-RED flow for ingesting IO-Link gateway telemetry, enriching it with contextual metadata, and persisting both real-time metrics and diagnostic logs into an InfluxDB + Grafana observability stack. It is tailored for industrial edge deployments where lightweight data collection, auditability, and rapid troubleshooting are critical.

## Prerequisites

Before importing the flow, ensure the following tooling and services are available:

- **Node-RED 3.1 or later** with the [`node-red-contrib-influxdb`](https://flows.nodered.org/node/node-red-contrib-influxdb) palette module installed.
- **InfluxDB 2.x** with buckets `A01`, `iot_events`, and `gateway_identification`, plus a token that grants write access to all three buckets.
- **Mosquitto (or compatible) MQTT broker** accessible from the Node-RED runtime.
- Access to create or mount directories for the structured HTTP/MQTT debug logs referenced by the flow (default: `E:\\NodeRed\\Logs`).
- Updated copies of the configuration dictionaries in this repository (`config/masterMap.json`, `config/errorCodes.json`).

## High-level architecture

The flow loads shared configuration on deploy, then runs two parallel ingestion paths that converge on InfluxDB writers:

1. **Configuration loaders** populate `global.errorMap` and `flow.cfg` with the error dictionary and IO-Link alias map from the JSON config files.
2. **HTTP polling pipeline** generates gateway IP targets, calls `/iolink/v1/gateway/events`, normalises event payloads (ports `x0`–`x7`, event state transitions, timestamps), and writes structured points to the `iot_events` bucket.
3. **Gateway identification poll** periodically queries `/iolink/v1/gateway/identification` to capture hardware and firmware metadata for the `gateway_identification` bucket.
4. **MQTT ingestion pipeline** subscribes to wildcard IO-Link topics, resolves measurement aliases from `flow.cfg`, and streams process data into the `A01` bucket.
5. **Structured logging taps** mirror each pipeline stage into JSON files for audit/debug, with a scheduled reset to keep the artefacts fresh.

See the [detailed flow walkthrough](docs/README.md) for node-by-node behavior, upgrade notes, and troubleshooting guidance.

## Repository tour

| Path | What you will find |
| --- | --- |
| `flows/` | Exported Node-RED flow definitions. The flagship flow, [`Influx_Data_Pipeline_v1.2.json`](flows/Influx_Data_Pipeline_v1.2.json), implements the dual HTTP/MQTT ingestion architecture described above. |
| `docs/` | In-depth documentation, including the [Flow guide](docs/README.md). |
| `config/` | Configuration dictionaries consumed by the flow. See `config/masterMap.json` (alias map) and `config/errorCodes.json` (error dictionary). |
| `docs/schemas/` | JSON Schemas that describe and validate the configuration dictionaries. |

### Configuration dictionaries

- **`config/masterMap.json`** – Maps IO-Link process, diagnostic, and statistical fields (e.g., `temperaturePin1`, `meanTemperature`) to concise aliases that form Influx measurement names.
- **`config/errorCodes.json`** – Enumerates numeric gateway event codes (hex and decimal) alongside human-readable messages used in alerts and dashboards.

### Validating configuration locally

Validate `config/masterMap.json` and `config/errorCodes.json` before deploying updated dictionaries:

```bash
npx --yes ajv-cli validate \
  -s docs/schemas/masterMap.schema.json \
  -d config/masterMap.json

npx --yes ajv-cli validate \
  -s docs/schemas/errorCodes.schema.json \
  -d config/errorCodes.json
```

These commands install `ajv-cli` on-demand via `npx`. For repeated validation during development, you can add the tool as a local dependency:

```bash
npm install --save-dev ajv-cli
npm run validate:config
```

Add the following npm script to your `package.json` if you prefer a shorthand command:

```json
"scripts": {
  "validate:config": "ajv validate -s docs/schemas/masterMap.schema.json -d config/masterMap.json && ajv validate -s docs/schemas/errorCodes.schema.json -d config/errorCodes.json"
}
```

### Overriding configuration in production

The defaults in `config/` are designed for quick evaluation. For production deployments:

- **Containerised Node-RED** – Mount a read-only volume at `/data/config` (or your chosen target) and update the File In nodes to point at the mounted `masterMap.json` and `errorCodes.json`. Keep the repository copies as templates.
- **Bare-metal / Windows service** – Place production-ready dictionaries in a secure directory (e.g., `D:\NodeRed\config\`) and adjust the File In node paths accordingly. Maintain the repo’s `config/` directory for version-controlled defaults.
- **Automated rollouts** – Export `config/masterMap.json` and `config/errorCodes.json` as ConfigMaps or environment-configured files and mount them into the runtime. This allows centralised updates without modifying the flow definition.

Keep both files under version control and redeploy the flow after any updates so the runtime context reflects the latest mappings.

### Troubleshooting configuration validation

| Symptom | Resolution |
| --- | --- |
| `data must have required property 'pins'` when validating `masterMap.json` | Ensure the root object contains a `pins` property and that it is spelled correctly. |
| `data/pins/temperature` fails with `must be string` errors | Check for nested objects that contain non-string values—aliases must be strings in every category. |
| Validation errors referencing `additionalProperties` | Remove unexpected top-level keys from the config files or extend the schema if a new section is intentional. |
| Error codes rejected because the key format is invalid | Use decimal integers (e.g., `6144`) or hexadecimal strings prefixed with `0x` (e.g., `0x9801`). |

## Next steps for contributors

- Review the [flow documentation](docs/README.md) to understand deployment expectations and operational tips.
- Read the [Contributing Guide](CONTRIBUTING.md) for exporting flows, formatting JSON, running validations, and documenting your work before opening a pull request.

## License

This project is distributed under the [Apache License 2.0](LICENSE).
