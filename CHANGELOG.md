# Changelog

All notable changes to the Industrial IoT Data Pipeline are documented in this file. Dates reflect when the flow definition and supporting assets were published to the repository.

## Unreleased
**Tag:** `vNext` — **Release Date:** TBD

- Documented every Node-RED node with rich info panels and inline Function comments to streamline on-call troubleshooting.
- Switched the project licensing from Apache 2.0 to MIT; downstream consumers should review the updated LICENSE file and ensure their compliance processes reflect the change.
- Expanded operator documentation with context reference tables, structured log catalogs, and schema-backed editing guidance to streamline maintenance tasks.
- Added Flux-based Grafana dashboard exports (`docs/grafana/`) covering gateway events and device inventory to accelerate observability rollout.

## v1.2 — 2024-02-15
**Tag:** `v1.2` — **Release Date:** 2024-02-15

- Unified the HTTP and MQTT pipelines with shared enrichment logic so operators get consistent alias resolution and tagging across ingestion paths.
- Added structured log rotation hooks and diagnostics that surface gateway heartbeat gaps before downstream alerts fire.
- Refreshed the exported flow (`Influx_Data_Pipeline_v1.2.json`) and updated documentation to reflect the new Grafana dashboards and validation tooling.

## v1.1 — 2023-09-08
**Tag:** `v1.1` — **Release Date:** 2023-09-08

- Introduced dedicated context initialization for configuration dictionaries to avoid stale IO-Link alias mappings after hot redeploys.
- Hardened MQTT topic filters and payload schema validation to prevent malformed messages from bypassing error handling nodes.
- Published a troubleshooting checklist focused on distinguishing gateway firmware faults from transport issues.

## v1.0 — 2023-04-21
**Tag:** `v1.0` — **Release Date:** 2023-04-21

- Initial public release of the IO-Link + InfluxDB pipeline with baseline HTTP polling, MQTT ingestion, and context dictionary loaders.
- Delivered the first exported flow (`Influx_Data_Pipeline_v1.0.json`) alongside default configuration dictionaries for evaluation deployments.
