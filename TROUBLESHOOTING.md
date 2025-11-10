# Industrial IoT Data Pipeline – Troubleshooting Guide

![Pipeline lifecycle](docs/pipeline-operations.svg)

## 1. How to use this guide
Use the tables below to quickly map observed symptoms to likely causes and recovery steps. Start with the pipeline lifecycle diagram to identify which stage (startup, steady state, observability) is affected, then follow the deep-dive procedures.

## 2. Quick symptom matrix
| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| No data in InfluxDB buckets | Invalid Influx credentials or bucket names; network reachability issues | Re-enter token and bucket names in InfluxDB config node; test reachability with `curl` or Influx UI. |
| MQTT router outputs `cfg not loaded yet` | `config/masterMap.json` failed to load or is invalid JSON | Validate file against schema (`ajv-cli`); confirm file path in File In node and ensure permissions allow read access. |
| HTTP poll returns 4xx/5xx errors | Gateway credentials incorrect, TLS mismatch, or IP range misconfigured | Verify gateway auth, adjust `generate IPs` ranges, and inspect gateway logs for blocked requests. |
| Structured logs missing or empty | Log directory does not exist or Node-RED lacks write permission | Create directory, adjust file node paths, and trigger **Log Reset** inject to recreate files. |
| Grafana dashboards show stale data | Flow not writing or queries outdated | Confirm Influx writes are succeeding, then update dashboard queries to reflect latest measurement names. |

## 3. Diagnostic procedures
1. **Validate configuration context**
   - Open `Menu → Context Data` in Node-RED and check `global.errorMap` and `flow.cfg`. If missing, redeploy and monitor Node-RED logs for file read errors.
   - Run schema validation using commands in `README.md` to ensure JSON structure is valid.
2. **Inspect HTTP pipeline**
   - Enable debug nodes after the HTTP request to view status codes and payloads.
   - Review `01_GET_*.json` files in the log directory for raw responses.
   - If TLS is required, attach a TLS config node and confirm certificates.
3. **Inspect MQTT pipeline**
   - Use `mosquitto_sub -v -t '+/iolink/v1/#'` from the Node-RED host to confirm frames are arriving.
   - Check `MQTT_raw_*.json` for captured frames and ensure alias mapping exists for new fields.
4. **Verify InfluxDB writers**
   - Review Node-RED debug sidebar for write errors.
   - In Influx UI, run Flux query `from(bucket:"iot_events") |> range(start: -15m) |> limit(n:5)` to confirm event ingestion.

## 4. Recovery playbooks
- **Configuration rollback** – Restore previous versions of `config/` files from version control, redeploy flow, and re-run schema validation.
- **Credential rotation** – Update InfluxDB token and MQTT credentials in Node-RED config nodes; deploy and confirm writes resume.
- **Gateway isolation** – Temporarily remove failing IPs from `generate IPs` list while investigating hardware issues.
- **Log directory restore** – Recreate missing directories and set permissions (`chmod 770` recommended); trigger **Log Reset** inject.

## 5. Escalation & support
- Document steps taken, include relevant log excerpts (`MQTT_raw_*`, `01_GET_*`), and attach screenshots of Grafana dashboards when escalating to engineering.
- Reference the developer contact protocol in `CONTRIBUTING.md` or project issue tracker when opening a ticket.

## 6. Related documentation
- Architecture context: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Operator tasks: [`USER_MANUAL.md`](USER_MANUAL.md)
- Flow walkthrough: [`docs/README.md`](docs/README.md)
