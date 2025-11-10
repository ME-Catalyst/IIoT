# Example Dashboards

This directory hosts reusable Grafana dashboard JSON templates. Import them to visualize the telemetry and metadata produced by
 the Industrial IoT data pipeline.

## Available Dashboards

| File | Description |
| --- | --- |
| `sample_configs/io-link-gateway-overview.json` | Operational summary of IO-Link gateway events, including event volume trends, latest state per port, average severity, and top recurring alarms. Uses the `iot_events` bucket produced by the HTTP event parser. |
| `sample_configs/io-link-device-inventory.json` | Inventory view that pivots the `device_info` measurement written by the gateway identification poll. Includes gateway counts, firmware distribution, and the most recent hardware metadata per device. |

## Usage

1. In Grafana, navigate to **Dashboards → Import**.
2. Upload the desired JSON file or paste its contents into the import form.
3. When prompted, select your Flux-enabled InfluxDB data source and confirm the default bucket name (`iot_events` or `gateway_identification`).
4. Save the dashboard. Repeat for additional JSON templates as needed.

These dashboards rely on Flux queries and require Grafana 9.0 or later with an InfluxDB data source configured against the same buckets that the Node-RED flow writes to.
