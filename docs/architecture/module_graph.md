# Module and Node Overview

The Industrial IoT data pipeline is implemented as a Node-RED project. Each logical module in the flow is represented by a group
d of nodes that encapsulate a discrete responsibility. This reference enumerates those modules and highlights how they interact.

| Module | Node-RED Group | Responsibility | Notes |
| --- | --- | --- | --- |
| Config Loader | `Config Loader Group` | Reads `config/masterMap.json` and `config/errorCodes.json` into Node-RED context on deploy. | Use the environment variable `CONFIG_BASE_PATH` to override file locations when packaging into containers. |
| HTTP Poller | `HTTP Poll Pipeline` | Queries `/iolink/v1/gateway/events` for each configured gateway. | Rate is controlled by the `Poll cadence` inject node (default: 60 seconds). |
| HTTP Event Parser | `Function v8` | Normalizes HTTP event payloads, resolving port names and timestamps. | Throws descriptive errors when required context is missing. |
| Identification Poll | `Gateway Identification` | Calls `/iolink/v1/gateway/identification` to capture metadata. | Emits inventory records and stores snapshots in structured logs. |
| MQTT Router | `IO-Link Router v10` | Consumes `+/iolink/v1/#` topics and maps payload fields via `cfg.pins`. | Publishes normalized measurements to the A01 bucket. |
| Influx Writers | `Write Influx`, `write to Influx (gateway_events)`, `Influx - gateway_identification` | Persists metrics, event history, and hardware metadata. | Ensure tokens have write permissions to `A01`, `iot_events`, and `gateway_identification`. |
| Log Reset & File Writers | `Log Reset`, `File Out` nodes | Maintains structured JSON archives of HTTP/MQTT payloads. | Rotate the log directory periodically to control growth. |

## Dependency Highlights

* Function nodes depend on context populated by the Config Loader. Deployments must include valid configuration files.
* Influx writers expect credentials defined in the Node-RED configuration nodes. Update them whenever tokens rotate.
* MQTT ingress requires network access to the edge broker. When running offline, disable the MQTT sub-flow to prevent errors.

For a process-level perspective, review `docs/architecture/data_flow.md`. Visual assets reside under `docs/visuals/diagrams/`.
