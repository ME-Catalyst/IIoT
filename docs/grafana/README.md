# Grafana dashboards

This directory contains example Grafana dashboards that visualise the Node-RED pipelines and supporting configuration shipped with this repository.

## Dashboards

| File | Description |
| --- | --- |
| `io-link-gateway-overview.json` | Operational summary of IO-Link gateway events, including event volume trends, the latest state per port, average severity, and the top recurring alarms. Uses the `iot_events` bucket produced by the HTTP error-event parser. |
| `io-link-device-inventory.json` | Inventory view that pivots the `device_info` measurement written by the gateway identification poll. Includes gateway counts, firmware distribution, and the most recent hardware metadata per device. |

## Usage

1. In Grafana, navigate to **Dashboards → Import**.
2. Upload the JSON file or paste its contents into the import form.
3. When prompted, select your Flux-enabled InfluxDB data source and confirm the default bucket name (`iot_events` or `gateway_identification`).
4. Save the dashboard. Repeat for the second JSON file if required.

Both dashboards rely on Flux queries and expect Grafana 9.0 or later with an InfluxDB data source configured against the same buckets that the Node-RED flow writes to.
