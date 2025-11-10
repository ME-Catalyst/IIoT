# Recovery Playbooks

## Restoring Connectivity Failures

1. Confirm network reachability between Node-RED and the MQTT/HTTP targets.
2. Restart the Node-RED service to rebuild the MQTT connection and re-run the HTTP injects.
3. Validate credentials stored in the configuration nodes and rotate tokens if expired.

## Reverting to a Previous Flow

1. Export the current flow for record keeping.
2. Import the prior JSON export from `src/flows/production/`.
3. Redeploy and confirm telemetry resumes in InfluxDB.
4. Update `CHANGELOG.md` with the rollback details.

## Recovering Corrupted Configuration

1. Restore `config/masterMap.json` and `config/errorCodes.json` from version control or backups.
2. Validate the restored files using the schemas under `docs/developer/examples/sample_configs/schemas/`.
3. Redeploy the flow to repopulate context.

## Incident Reporting

* Document the root cause, impacted gateways, and mitigation steps in the internal incident tracker.
* Attach relevant structured logs and Grafana screenshots stored under `docs/visuals/`.
* Schedule a follow-up to update automation or monitoring gaps identified during the incident.
