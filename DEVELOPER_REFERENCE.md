# Industrial IoT Data Pipeline – Developer Reference

## 1. Purpose
This document orients contributors who maintain the Node-RED flow, configuration dictionaries, and supporting assets. It complements the user-focused manual and codifies expectations for coding standards, validation, and release preparation.

## 2. Repository layout
| Path | Description |
| --- | --- |
| `flows/` | Versioned Node-RED flow exports (`Influx_Data_Pipeline_v1.2.json`). |
| `config/` | Runtime configuration dictionaries (`masterMap.json`, `errorCodes.json`). |
| `docs/` | Flow walkthrough, changelog, schemas, Grafana dashboards, and architecture assets. |
| `docs/schemas/` | JSON Schemas enforcing dictionary structure. |
| `docs/grafana/` | Importable Grafana dashboards. |
| `RELEASE.md` | Release engineering checklist. |
| `README.md` | Quick-start and repository overview. |

## 3. Flow components
- **HTTP pipelines** – Located in groups labelled `6bd20502…`; ensure Function nodes remain idempotent and stateless outside of deliberate context usage.
- **MQTT router (Function v10)** – Uses `flow.cfg.pins` for aliasing; when adding new metrics, confirm corresponding alias exists.
- **Identification poll** – Group `59c49ae82e…`; maintain alignment with `gateway_identification` bucket schema.
- **Structured logging taps** – Mirror HTTP/MQTT traffic; keep filenames descriptive and consistent for log rotation tooling.

## 4. Coding conventions
- Keep Function node code pure JavaScript without external dependencies; rely on Node-RED context for shared state.
- Normalize port identifiers to `x0`–`x7` and ensure timestamps are ISO strings before writing to InfluxDB.
- When introducing new buckets or measurements, document them in `docs/README.md` and update Grafana dashboards.
- Maintain JSON indentation at two spaces and alphabetize object keys where practical to reduce diff churn.

## 5. Validation workflow
1. **Schema validation** – Run the `ajv-cli` commands from `README.md` whenever modifying `config/` files.
2. **Flow diffs** – Compare flow exports using `npx --yes json-diff flows/Influx_Data_Pipeline_v1.1.json flows/Influx_Data_Pipeline_v1.2.json` (adjust versions) to review structural changes.
3. **Runtime smoke test** – Import updated flow into a staging Node-RED instance, confirm context loaders execute, and check structured logs write successfully.
4. **Grafana verification** – Import dashboards and ensure new measurements appear; update panels if measurement names change.

## 6. Release management
- Follow `RELEASE.md` for tagging, packaging flow JSON, and updating documentation.
- Summarize behavior changes in `docs/CHANGELOG.md` and align version numbers across flow export and documentation headers.
- Coordinate with operations to update production configuration mounts and tokens.

## 7. Tooling roadmap for developers
- Add npm scripts (`validate:config`, `diff:flows`) to streamline routine checks.
- Explore automated payload replay tests using stored MQTT/HTTP samples.
- Investigate GitHub Actions to enforce schema validation on pull requests.

## 8. Helpful references
- Architecture overview: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Operations lifecycle diagram: [`docs/pipeline-operations.svg`](docs/pipeline-operations.svg)
- Troubleshooting playbook: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
