# Known Issues

| Issue | Symptoms | Resolution |
| --- | --- | --- |
| InfluxDB writes fail with `unauthorized access` | Debug sidebar shows 401 responses from the InfluxDB Out nodes. | Regenerate the token with write access to `A01`, `iot_events`, and `gateway_identification`. Update the credentials in Node-RED and redeploy. |
| MQTT ingest stalls after deploy | MQTT status node reports repeated disconnects. | Confirm broker reachability and credentials. Disable the MQTT sub-flow when operating offline. |
| Gateway inventory missing entries | Grafana dashboard shows blank device metadata. | Ensure the identification poll inject is enabled and HTTP access to `/iolink/v1/gateway/identification` is permitted through firewalls. |
| Configuration context is empty | Function nodes throw `cfg missing` errors. | Verify `config/masterMap.json` and `config/errorCodes.json` exist and are valid JSON. Review `docs/user/install_guide.md` for schema validation steps. |
