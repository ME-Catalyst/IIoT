# Industrial IoT Data Pipeline – Developer Reference

## 1. Purpose
This document orients contributors who maintain the Node-RED flow, configuration dictionaries, and supporting assets. It complem
ents the user-focused manual and codifies expectations for coding standards, validation, and release preparation.

## 2. Repository Layout
| Path | Description |
| --- | --- |
| `src/` | Runtime assets, including production Node-RED exports under `src/flows/production`. |
| `flows/` | Export-ready flow snapshots with full inline documentation. |
| `examples/` | Version-tagged sanitized flow variants and configuration samples for local exploration. |
| `tests/` | Structural validation scripts and schemas (`python -m tests.validate_flows`). |
| `config/` | Runtime configuration dictionaries (`masterMap.json`, `errorCodes.json`). |
| `docs/` | Structured documentation tree for architecture, user, developer, troubleshooting, and visuals. |
| `docs/developer/examples/` | Grafana dashboards, sample configs, demo scripts, and schemas. |
| `RELEASE.md` | Release engineering checklist. |
| `README.md` | Quick-start and repository overview. |

## 3. Flow Components
- **HTTP pipelines** – Located in groups labelled `6bd20502…`; ensure Function nodes remain idempotent and stateless outside of deliberate context usage.
- **MQTT router (Function v10)** – Uses `flow.cfg.pins` for aliasing; when adding new metrics, confirm corresponding alias exists.
- **Identification poll** – Group `59c49ae82e…`; maintain alignment with `gateway_identification` bucket schema.
- **Structured logging taps** – Mirror HTTP/MQTT traffic; keep filenames descriptive and consistent for log rotation tooling.

Detailed module descriptions are available in [`docs/architecture/module_graph.md`](docs/architecture/module_graph.md).

### Flow Components at a Glance

```mermaid
mindmap
  root((Flow Components))
    "Config Loader\nGroup: Config Loader Group\nSource: config/masterMap.json + config/errorCodes.json (honors CONFIG_BASE_PATH)\nPrereq: CONFIG_BASE_PATH env overrides file path, Node-RED file access\nOutput: global.cfg.*, global.errorCodes contexts"
      "Feeds context to downstream modules"
    "HTTP Poller\nGroup: HTTP Poll Pipeline\nSource: /iolink/v1/gateway/events\nPrereq: Poll cadence inject + gateway list from flow/global context\nOutput: raw HTTP events -> Function v8"
    "HTTP Event Parser\nGroup: Function v8\nSource: HTTP events from poller\nPrereq: global.cfg.pins + errorCodes context\nOutput: normalized payloads -> Write Influx + log taps"
    "Identification Poll\nGroup: Gateway Identification\nSource: /iolink/v1/gateway/identification\nPrereq: gateway list in context, credentials for HTTP nodes\nOutput: inventory snapshots -> Influx - gateway_identification + structured logs"
    "MQTT Router\nGroup: IO-Link Router v10\nSource: +/iolink/v1/# topics\nPrereq: flow.cfg.pins context, broker credentials, network reachability\nOutput: normalized MQTT metrics -> Write Influx (A01 bucket)"
    "Influx Writers\nGroups: Write Influx, write to Influx (gateway_events), Influx - gateway_identification\nSource: normalized payloads from Function v8 + IO-Link Router v10 + Gateway Identification\nPrereq: Influx credentials/tokens in config nodes\nOutput: A01, iot_events, gateway_identification buckets"
    "Log Reset & File Writers\nNodes: Log Reset + File Out\nSource: mirrored HTTP/MQTT payloads\nPrereq: writable log directory + rotation schedule\nOutput: structured JSON archives for audits"
```

## 4. Coding Conventions
- Keep Function node code pure JavaScript without external dependencies; rely on Node-RED context for shared state.
- Keep each Node-RED node's **info** panel current and annotate Function nodes with inline comments that explain logic and edge cases.
- Normalize port identifiers to `x0`–`x7` and ensure timestamps are ISO strings before writing to InfluxDB.
- When introducing new buckets or measurements, document them in [`docs/architecture/data_flow.md`](docs/architecture/data_flow.md) and update Grafana dashboards.
- Maintain JSON indentation at two spaces and alphabetize object keys where practical to reduce diff churn.

## 5. Validation Workflow
1. **Schema validation** – Run the `ajv-cli` commands from [`docs/user/install_guide.md`](docs/user/install_guide.md) whenever modifying `config/` files.
2. **Flow diffs** – Compare flow exports using `npx --yes json-diff src/flows/production/Influx_Data_Pipeline_v1.1.json src/flows/production/Influx_Data_Pipeline_v1.2.json` (adjust versions) to review structural changes.
3. **Runtime smoke test** – Import updated flow into a staging Node-RED instance, confirm context loaders execute, and check structured logs write successfully.
4. **Grafana verification** – Import dashboards from `docs/developer/examples/sample_configs/` and ensure new measurements appear; update panels if measurement names change.

## 6. Release Management
- Follow `RELEASE.md` for tagging, packaging flow JSON, and updating documentation.
- Summarize behavior changes in `CHANGELOG.md` and align version numbers across flow exports and documentation headers.
- Coordinate with operations to update production configuration mounts and tokens.

## 7. Managing Example Assets
- **Mirror release tags** – For every production flow tagged `vX.Y`, create matching folders under `examples/flows/vX.Y/` and `examples/config/vX.Y/`. Name the files with the same suffix (for example `sanitized_data_pipeline_v1.2.json`) so operators can confirm provenance quickly.
- **Redact before publishing** – Strip credentials, server addresses, and tokens from the example flow. Replace them with descriptive placeholders while keeping node wiring, context keys, and function logic intact.
- **Document updates** – Whenever you add or refresh example assets, update the user manual and this reference to call out availability and usage so downstream teams know which artifacts map to which releases.
- **Validate structure** – Run schema validation against the example configuration dictionaries to ensure they continue to round-trip through the same tooling as production files.

## 8. Tooling Roadmap for Developers
- Add npm scripts (`validate:config`, `diff:flows`) to streamline routine checks.
- Explore automated payload replay tests using stored MQTT/HTTP samples.
- Investigate GitHub Actions to enforce schema validation on pull requests.

## 9. Helpful References
- Architecture overview: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Data flow walkthrough: [`docs/architecture/data_flow.md`](docs/architecture/data_flow.md)
- Troubleshooting playbook: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- Logs and diagnostics: [`docs/troubleshooting/logs_and_diagnostics.md`](docs/troubleshooting/logs_and_diagnostics.md)
