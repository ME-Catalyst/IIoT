# Industrial IoT Data Pipeline – Roadmap

## 1. Product Vision
- Deliver a resilient, auditable IO-Link telemetry ingestion stack for edge factories that streams HTTP and MQTT data into a unif
ied InfluxDB observability plane.
- Provide operations-ready tooling (structured logs, Grafana dashboards, validation scripts) that shortens time-to-diagnosis when gateways drift or firmware evolves.
- Maintain low-touch upgrades for Node-RED operators by shipping versioned flow exports, schema-validated configuration dictionaries, and guided release notes.

## 2. Current Release Status
- **Latest flow**: `Influx_Data_Pipeline_v1.2.json` (dual HTTP/MQTT ingestion, identification poll, structured logging reset).
- **Supported platforms**: Node-RED ≥ 3.1, InfluxDB 2.x, Mosquitto-compatible MQTT brokers.
- **Operational baseline**: Configuration dictionaries stored under `config/`, context loaders populate `global.errorMap` and `flow.cfg`, Grafana dashboards available in `docs/developer/examples/sample_configs/`.

## 3. Near-term Goals (0–3 months)
The mermaid timeline below highlights how telemetry, observability, and platform initiatives align with the next 12 months; review it alongside each goal list for quick prioritisation context.

```mermaid
timeline
    title Initiative timeline by theme
    0-3 months : Expand telemetry coverage
    0-3 months : Tighten observability
    0-3 months : Smooth platform upgrades
    3-6 months : Edge platform packaging
    3-6 months : Observability automation (replay testing)
    3-6 months : Telemetry context externalisation
    6-12 months : Platform-level edge-to-cloud sync
    6-12 months : Telemetry-driven fleet insights
    6-12 months : Observability plug-in ecosystem
    classDef telemetry fill:#68c1ff,stroke:#0b3d91,color:#0b3d91
    classDef observability fill:#ffd166,stroke:#7c4700,color:#7c4700
    classDef platform fill:#95d5b2,stroke:#1b4332,color:#1b4332
    class "Expand telemetry coverage","Telemetry context externalisation","Telemetry-driven fleet insights" telemetry
    class "Tighten observability","Observability automation (replay testing)","Observability plug-in ecosystem" observability
    class "Smooth platform upgrades","Edge platform packaging","Platform-level edge-to-cloud sync" platform
```

1. **Expand telemetry coverage** – Add IO-Link statistics aliases to `config/masterMap.json` as devices ship new registers; update flow router to persist them automatically.
2. **Tighten observability** – Ship prebuilt Grafana alert rules alongside dashboards; extend structured log set with retention automation.
3. **Smooth upgrades** – Script JSON schema validation + flow export diff checks as npm scripts to lower friction for contributors.

## 4. Mid-term Initiatives (3–6 months)
Review the same timeline above when sequencing these mid-term milestones.

1. **Edge packaging** – Provide Docker Compose and Kubernetes manifests that wire Node-RED, Mosquitto, and InfluxDB with secure defaults.
2. **Context externalisation** – Investigate remote storage for `errorMap` and `masterMap` to support stateless Node-RED deployments.
3. **Automated replay testing** – Capture golden MQTT/HTTP payloads and replay them during CI to catch parser regressions.

## 5. Long-term Vision (6–12 months)
Keep cross-referencing the timeline to ensure long-term bets stay balanced with the short- and mid-term initiatives.

1. **Fleet insights** – Enrich Grafana dashboards with anomaly detection panels powered by Flux tasks or external analytics engines.
2. **Plug-in ecosystem** – Publish reusable Node-RED subflows for IO-Link normalization, making the pipeline extensible to other factories.
3. **Edge-to-cloud sync** – Explore replicating key metrics to a central cloud tenancy while preserving edge autonomy and offline durability.

## 6. Risks and Mitigations
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Gateway firmware changes field names unexpectedly | HTTP/MQTT parsing fails or produces sparse metrics | Maintain rigorous change control on `config/masterMap.json`; add replay fixtures in automated tests. |
| InfluxDB bucket credentials rotate without notice | Data ingestion halts silently | Document secret rotation in operator runbooks; add Grafana alert for zero-write periods. |
| Structured log directory unavailable | Debug history lost | Include path verification checks in deployment checklists; allow configurable fallback paths. |

## 7. Dependencies & Key Dates
- `CHANGELOG.md` tracks release history; align roadmap checkpoints with tagged flow exports.
- Coordinate roadmap updates with quarterly flow reviews to confirm the Node-RED runtime still matches repository defaults.
