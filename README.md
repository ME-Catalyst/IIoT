# Murr Elektronik Impact67 Pro IO Link Master IoT Data Pipeline

Production-ready Node-RED flows that collect IO-Link telemetry, enrich it with contextual metadata, and deliver normalized metrics to an InfluxDB + Grafana observability stack.

> **No Warranty or Liability** – Provided “as-is,” without warranty of any kind.

## Overview

* Dual ingestion paths (HTTP polling + MQTT subscribe) keep process metrics and gateway diagnostics in sync.
* Structured JSON logs mirror every stage for traceability and compliance.
* Reusable Grafana dashboards accelerate deployment across multiple facilities.

## Quickstart

1. Review the detailed installation steps in [`docs/user/install_guide.md`](docs/user/install_guide.md).
2. Import `src/flows/production/Influx_Data_Pipeline_v1.2.json` into Node-RED (**Menu → Import → Clipboard**).
3. Configure the InfluxDB and MQTT credentials, then deploy the flow.
4. Validate metrics using the Grafana templates under
   [`docs/developer/examples/sample_configs/`](docs/developer/examples/sample_configs/).

## Visual Reference

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontFamily': '"Inter","Segoe UI","Helvetica Neue",Arial,sans-serif', 'fontSize': '16px', 'primaryColor': '#f1f5f9', 'primaryBorderColor': '#1e293b', 'lineColor': '#1e293b', 'secondaryColor': '#e2e8f0', 'tertiaryColor': '#cbd5f5'}}}%%
flowchart LR
    Edge["Edge IO-Link Gateways\n\u2022 REST endpoints\n\u2022 /iolink/v1/gateway/events\n\u2022 /iolink/v1/gateway/identification\n\u2022 Identification metadata\n\u2022 MQTT telemetry topics"]
    subgraph NodeRED["Node-RED Runtime (Edge)"]
        direction TB
        HTTP["HTTP Event Poll Pipeline\nTransforms REST payloads"]
        MQTT["MQTT Ingest Pipeline\nNormalizes telemetry topics"]
    end
    subgraph Context["Runtime Context & Logging"]
        direction TB
        Config["Config Loaders\nmasterMap.json \u00b7 errorCodes.json"]
        Logs["Structured File Logs & Reset"]
    end
    Influx["InfluxDB 2.x Buckets\n\u2022 iot_events (HTTP event stream)\n\u2022 gateway_identification (HTTP metadata)\n\u2022 A01 (MQTT telemetry)"]
    Grafana["Grafana Dashboards\nVisualize metrics, events, inventory"]

    Edge --> HTTP
    Edge --> MQTT
    HTTP -->|iot_events| Influx
    HTTP -->|gateway_identification| Influx
    MQTT -->|A01 bucket| Influx
    Config --> HTTP
    Config --> MQTT
    HTTP -.->|Structured logs| Logs
    MQTT -.->|Structured logs| Logs
    Config --> Logs
    Influx -->|Flux queries| Grafana
```

## Documentation Map

| Guide | Purpose |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | High-level system structure and integration map with references into `/docs/architecture/`. |
| [`USER_MANUAL.md`](USER_MANUAL.md) | Comprehensive operator guide covering setup, validation, and lifecycle tasks. |
| [`DEVELOPER_REFERENCE.md`](DEVELOPER_REFERENCE.md) | Contributor workflow, internal APIs, and testing requirements. |
| [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | Symptom-driven diagnostics with recovery playbooks. |
| [`ROADMAP.md`](ROADMAP.md) | Milestones and planned releases. |
| [`CHANGELOG.md`](CHANGELOG.md) | Versioned history of shipped updates. |

Additional resources live under [`/docs`](docs/) and follow the structured layout described in [`ARCHITECTURE.md`](ARCHITECTURE
.md).

## Repository Layout

| Path | Description |
| --- | --- |
| `src/` | Production Node-RED exports and shared utilities. |
| `examples/` | Sanitized flow samples for demos and training. |
| `config/` | Configuration dictionaries consumed by the flows. |
| `tests/` | Validation utilities for flow JSON and schemas. |
| `docs/` | Supplemental documentation, diagrams, dashboards, and troubleshooting guides. |
