# Installation Guide

Follow these steps to import and run the Industrial IoT Node-RED flow on a fresh environment.

## 1. Provision Dependencies

1. Install **Node-RED 3.1 or later** on the target host.
2. Add the palette modules:
   * [`node-red-contrib-influxdb`](https://flows.nodered.org/node/node-red-contrib-influxdb)
3. Ensure the host can reach the site MQTT broker and InfluxDB instance.

## 2. Prepare Configuration Files

1. Copy `config/masterMap.json` and `config/errorCodes.json` into the Node-RED project directory.
2. Validate the files using the JSON Schemas located in `docs/developer/examples/sample_configs/schemas/`:
   ```bash
   npx --yes ajv-cli validate \
     -s docs/developer/examples/sample_configs/schemas/masterMap.schema.json \
     -d config/masterMap.json

   npx --yes ajv-cli validate \
     -s docs/developer/examples/sample_configs/schemas/errorCodes.schema.json \
     -d config/errorCodes.json
   ```

## 3. Import the Flow

1. Open the Node-RED editor and select **Menu → Import → Clipboard**.
2. Paste the contents of `src/flows/production/Influx_Data_Pipeline_v1.2.json` and click **Import**.
3. For redacted references, review `examples/flows/` in this repository.

## 4. Configure Connections

1. Open the **InfluxDB** configuration nodes and supply the host URL, organization, bucket names, and token.
2. Update the **Local MQTT** configuration node with the broker URL and credentials.
3. Adjust file node paths if your log directory is not `E:\NodeRed\Logs`.

## 5. Deploy and Verify

1. Click **Deploy** in the Node-RED editor.
2. Confirm that `global.errorMap` and `flow.cfg` are populated via **Menu → Context Data**.
3. Verify that data arrives in the `A01`, `iot_events`, and `gateway_identification` buckets within InfluxDB.
4. Load the Grafana dashboards located under `docs/developer/examples/sample_configs/` to validate visualization bindings.

## 6. Post-Installation Tasks

* Schedule periodic backups of `config/` and the structured log directory.
* Document the InfluxDB token scope and rotation policy in your operations runbook.
* Monitor Node-RED runtime logs to capture connection errors or misconfigured credentials.
