# Industrial IoT Data Pipeline

This repository contains a production-ready Node-RED flow for ingesting IO-Link gateway telemetry, enriching it with contextual metadata, and persisting both real-time metrics and diagnostic logs into an InfluxDB + Grafana observability stack. It is tailored for industrial edge deployments where lightweight data collection, auditability, and rapid troubleshooting are critical.

## Prerequisites

Before importing the flow, ensure the following tooling and services are available:

- **Node-RED 3.1 or later** with the [`node-red-contrib-influxdb`](https://flows.nodered.org/node/node-red-contrib-influxdb) palette module installed.
- **InfluxDB 2.x** with buckets `A01`, `iot_events`, and `gateway_identification`, plus a token that grants write access to all three buckets.
- **Mosquitto (or compatible) MQTT broker** accessible from the Node-RED runtime.
- Access to create or mount directories for the structured HTTP/MQTT debug logs referenced by the flow (default: `E:\\NodeRed\\Logs`).
- Updated copies of the configuration dictionaries in this repository (`masterMap.json`, `errorCodes.json`).

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
| `docs/` | In-depth documentation, including the [Flow guide](docs/README.md). Future additions such as `CONTRIBUTING.md` and `TESTING.md` will land here to describe collaboration and verification practices. |
| `masterMap.json` | IO-Link alias map loaded into `flow.cfg` to translate raw gateway fields into human-friendly measurement names. |
| `errorCodes.json` | Gateway event/error dictionary loaded into `global.errorMap` so the flow can enrich event payloads with descriptive text. |

### Configuration dictionaries

- **`masterMap.json`** – Maps IO-Link process, diagnostic, and statistical fields (e.g., `temperaturePin1`, `meanTemperature`) to concise aliases that form Influx measurement names.
- **`errorCodes.json`** – Enumerates numeric gateway event codes (hex and decimal) alongside human-readable messages used in alerts and dashboards.

Keep both files under version control and redeploy the flow after any updates so the runtime context reflects the latest mappings.

## Next steps for contributors

- Review the [flow documentation](docs/README.md) to understand deployment expectations and operational tips.
- Check back for upcoming `docs/CONTRIBUTING.md` and `docs/TESTING.md` guides; until then, please document any local testing steps directly in your pull requests.

## License

This project is distributed under the [Apache License 2.0](LICENSE).
