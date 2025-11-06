# Influx Data Pipeline v1.2 – Node‑RED Flow

> **Flow file:** `Influx_Data_Pipeline_v1.2.json`
> **Last reviewed:** 2025‑03‑27

This flow ingests IO‑Link gateway data through two independent paths (HTTP polling & MQTT subscribe), enriches it with metadata, writes structured points to InfluxDB 2.x, and archives full frames for audit/debug.  It is designed for **industrial edge deployments** where on‑prem Node‑RED acts as a lightweight collector in a Mosquitto / Influx / Grafana stack.

> ℹ️ **What’s new in v1.2**
>
> * Added an identification poll that writes gateway make/model metadata into a new Influx bucket `gateway_identification`—create the bucket (or disable the writer) before upgrading from v1.0.
> * Upgraded the HTTP error-event parser (Function v8) to emit normalised port names (`x0`–`x7`), event state (`event_start`/`event_stop`), and raw device timestamps; dashboards that key off the old port strings must be updated.
> * Replaced the ad-hoc debug dumps with structured log files (`MQTT_raw_*`, `MQTT_discard_*`, `01_GET_*`, etc.) driven by a new “Log Reset” inject plus wildcard MQTT taps (`#`, `$SYS/#`). Confirm the Node-RED service account can overwrite the new file set.


---

## 1. Quick‑start

| Step | Action |
| --- | --- |
| **1** | Install **Node‑RED ≥ 3.1** and the palette modules:<br/>`node-red-contrib-influxdb` *(Influx 2.x writer)*. |
| **2** | Copy the supporting config files:<br/>`config/masterMap.json` (IO‑Link alias map)<br/>`config/errorCodes.json` (event/error dictionary). |
| **3** | Import the flow JSON into the Node‑RED editor (`Menu → Import → Clipboard`). |
| **4** | Provision InfluxDB targets: ensure buckets **A01**, **iot_events**, and new **gateway_identification** exist and the token assigned to the `InfluxDB` node can write to all three. |
| **5** | Double‑click the **InfluxDB** and **Local MQTT** config nodes to enter credentials/hostnames, then adjust the file node paths if your log directory is not `E:\NodeRed\Logs`. |
| **6** | Click **Deploy**. On startup the config injects load the maps, the identification poll seeds `gateway_identification`, and the **Log Reset** inject truncates the structured debug files. |


---

## 2. High‑level architecture

```text
                +-------------------+
                | config/masterMap.json |
                | config/errorCodes.json |
                +---------+---------+
                          |
                          v  (startup inject)
          +---------------------------+
          |  Config Loader Group      |
          +---------------------------+
                          |
        global.errorMap   |   flow.cfg
                          |
            ┌─────────────┴───────────────┐
            │                             │
            │                             │
   HTTP Poll Pipeline              MQTT Ingest Pipeline
   (Group: 6bd2...)                (Group: 30ec...)
            │                             │         
            │                             │         
    GET /gateway/events       +/iolink/v1/#
            │                             │
            ▼                             ▼
   decode & tidy          IO‑Link router (v10)
            |                             |
            +-----------+-----------------+
                        |
                        ▼
                 InfluxDB 2.x
                        |
                        ▼
                   Grafana 12 OSS
```

* **Config Loader Group** – Loads `errorCodes.json` into global context and `masterMap.json` into flow context (`cfg`) on startup.
* **HTTP Poll Pipeline** – Generates IP targets, polls `/iolink/v1/gateway/events` every 60 s (default), and runs the v8 event parser that normalises port IDs (`x0`–`x7`), state transitions, and timestamps before handing off to Influx.
* **Gateway identification poll** – On deploy, calls `/iolink/v1/gateway/identification` for each host and persists make/model metadata via the `All messages to Influx` function.
* **MQTT Ingest Pipeline** – Subscribes to all IO‑Link frames, resolves aliases via `cfg.pins`, and flattens data for storage.
* **InfluxDB Out** – Three writers:

  * `Write Influx` → bucket **A01** (process / diagnostics / statistics / etc.)
  * `write to Influx (gateway_events)` → bucket **iot_events** (event log)
  * `Influx - gateway_identification` → bucket **gateway_identification** (gateway inventory)
* **File Logs & bus taps** – Structured JSON dumps for HTTP and MQTT paths (`01_GET_*.json`, `MQTT_raw_*.json`, wildcard topics `#`/`$SYS/#`) plus a **Log Reset** inject that truncates them on deploy.


---

## 3. Flow tour (node-by-node)

### 3.1 Configuration loaders

| Node | Purpose |
| --- | --- |
| **Load errorCodes.json** (inject) | Fires once at boot. |
| **Read errorCodes.json** (file in) | Reads the dictionary; output is UTF‑8 string. |
| **Parse to Object** (json) | Converts to JS object. |
| **Store in global.errorMap** (function) | Saves to global context for later lookup. |
| **Load masterMap.json** (inject) | Similar pattern for gateway pin/metric alias map. |
| **Read config JSON → parse → save cfg** | Stores to `flow.cfg` so the router can apply field aliases. |

### 3.2 HTTP event polling (`6bd20502…`)

1. **trigger** *(inject)* – Fires 5 s after deploy then every 60 s (editable).<br>
2. **generate IPs** – Returns one msg per IP as `{ payload:"192.168.1.6", ip:"192.168.1.6" }`. Edit the `ranges` array to match your LAN.
3. **build HTTP URL** – Appends `/iolink/v1/gateway/events` and stores in `msg.url`.
4. **GET gateway events** *(http request)* – Parses JSON response (`ret:obj`). On error, `statusCode` is set and downstream logic drops the message.
5. **tag IP / error handling** – Adds `msg.ip`, filters out 4xx/5xx.
6. **split events array** – Breaks the returned list so each event is processed separately.
7. **Influx data prep** *(function v8)* – Normalises port IDs to `x0`–`x7`, derives `eventState`, enriches with `rawDeviceTimestamp`, and looks up `errorDescription` from `global.errorMap`.
8. **Influx - gateway_events** – Inserts into **iot_events** bucket, measurement `gateway_events`.

### 3.3 Gateway identification poll (`59c49ae82e…`)

1. **trigger** *(inject)* – Runs once on deploy, then every 10 minutes.
2. **generate IPs** – Reuses the same IP generator to iterate targets.
3. **build HTTP URL** – Points at `/iolink/v1/gateway/identification`.
4. **GET gateway identification** *(http request)* – Retrieves hardware/firmware metadata; failures are dropped.
5. **All messages to Influx** – Wraps the full payload (serial, vendor, firmware, etc.) into a `device_info` measurement with nanosecond timestamps.
6. **Influx - gateway_identification** – Writes to the new **gateway_identification** bucket.

### 3.4 MQTT ingestion group (`30ecd298…`)

1. **All IO‑Link topics** *(mqtt in)* – Wildcard subscription `+/iolink/v1/#` with QoS 1.
2. **IO‑Link router** – Detects section (`processdata`, `diagnostics`, `statistics`, `events`, …), resolves aliases from `cfg.pins`, and emits one point per mapped field. Output 1/2 feed the log groups.
3. **Write Influx** – Writes to **A01** bucket using dynamic measurement name `${head}_${portTag}_${alias}`.

### 3.5 HTTP request logging (`b985c3ba5e55…`)

* **Log Reset** *(inject)* – Truncates HTTP log files on deploy and every 48 h.
* **Serialize Full Message** nodes – Capture the pipeline at each stage into `E:\NodeRed\Logs\01_GET_request.json`, `02_GET_reply.json`, `03_GET_tag.json`, `04_GET_split.json`, and `05_GET_influx.json` (plus matching `_v` versions containing verbose payloads).

### 3.6 MQTT logging & broker taps (`d82d2374faff…`)

* **Log Reset** *(inject)* – Clears MQTT log files on deploy and every 48 h.
* **Serialize Full Message** nodes – Persist raw MQTT inputs, router outputs, discarded frames, and Influx-ready payloads to `MQTT_raw_input*.json`, `MQTT_raw_frames*.json`, `MQTT_discard_frames*.json`, and `MQTT_Influx*.json`.
* **mqtt in `#` / `$SYS/#`** – Optional broker-wide taps that mirror all topics into the structured log set for diagnostics.

### 3.7 Context reference

| Context scope | Key | Source node | Purpose |
| ------------- | --- | ----------- | ------- |
| `global` | `errorMap` | **Store in global.errorMap** | Lookup table for translating gateway event codes into human-readable strings before writing to Influx or emitting alerts. |
| `flow` | `cfg` | **Read config JSON → parse → save cfg** | Alias dictionary for MQTT router and HTTP event parser. Contains nested objects keyed by metric group (for example `pins.temperature`). |
| `flow` | `logDirectory`* | (Function constants inside logging tabs) | Shared base path used when writing structured JSON debug artefacts. Update alongside File Out nodes if you relocate logs. |

> \*The logging groups derive `logDirectory` from constants in their Function nodes. Search for `E:\\NodeRed\\Logs` inside the flow if you need to change the path globally.

On a fresh deploy, confirm both context entries populate by opening **Menu → Context Data** in the Node-RED editor. Empty context suggests a missing configuration file, schema violation, or file permission issue.


---

## 4. End-to-end verification playbook

Follow this checklist to validate that the gateways are reachable, the brokers are emitting data, and the flow still enriches frames before they are written to disk or InfluxDB.

### 4.1 MQTT ingress smoke test

1. **Confirm broker reachability**
   ```bash
   mosquitto_sub -h <mqtt-host> -p 1883 -t "$SYS/broker/version" -C 1
   ```
   This lightweight probe ensures your credentials and TLS settings (if enabled) are accepted before subscribing to the production topics.

2. **Watch the IO-Link namespace**
   ```bash
   mosquitto_sub -h <mqtt-host> -p 1883 -u <user> -P '<password>' \
     -t '+/iolink/v1/#' -v | jq '.'
   ```
   Leave this running while triggering sensor activity. You should see JSON payloads containing `head`, `port`, and `timestamp` fields.

3. **Check discard feed for schema drift**
   ```bash
   mosquitto_sub -h <mqtt-host> -p 1883 -u <user> -P '<password>' \
     -t 'debug/iot/MQTT_discard_frames' -v -C 10 | jq '.'
   ```
   Non-empty output indicates frames the router could not map (for example, unknown aliases). Investigate before promoting the change.

### 4.2 HTTP poll verification

1. **Validate `/gateway/events` endpoint**
   ```bash
   curl -sS http://<gateway-ip>/iolink/v1/gateway/events | jq '.'
   ```
   Expect an array of event objects. If the call fails, the HTTP pipeline will drop the message and you will only see errors in the structured logs.

2. **Verify identification poll**
   ```bash
   curl -sS http://<gateway-ip>/iolink/v1/gateway/identification | jq '.'
   ```
   The response should include `vendorName`, `productCode`, and `firmwareVersion`—values that the flow forwards to the `gateway_identification` bucket.

3. **Run curl through the Node-RED host**
   ```bash
   curl -sS -H 'X-Debug: pipeline' http://localhost:1880/io-test/health
   ```
   (Optional) Use this if you have exposed a local test HTTP-In node that fans into the same parser. It confirms the Node-RED container has outbound egress to the gateways.

### 4.3 Message path validation

| Step | Expected signal |
| ---- | ---------------- |
| **MQTT** | `mosquitto_sub` shows live traffic on `+/iolink/v1/#` and zero (or temporary) entries on `debug/iot/MQTT_discard_frames`. |
| **HTTP** | `curl` requests return JSON arrays/objects with a 200 status. |
| **Influx** | Check the bucket dashboards or use the `/api/v2/query` endpoint to confirm new timestamps appear after the MQTT/HTTP probes. |

### 4.4 Structured log catalogue

| File prefix | Source group | What it captures | Why it matters |
| ----------- | ------------ | ---------------- | -------------- |
| `01_GET_request*.json` | HTTP pipeline | Raw request metadata and target URL list. | Confirms the IP generator and URL builder produced the expected targets. |
| `02_GET_reply*.json` | HTTP pipeline | Gateway responses prior to parsing. | Identify HTTP status codes, authentication failures, or malformed JSON before the parser runs. |
| `03_GET_tag*.json` / `04_GET_split*.json` | HTTP pipeline | Events after tagging with IP metadata and after array splitting. | Verify event fan-out and per-host attribution. |
| `05_GET_influx*.json` | HTTP pipeline | Final Influx payloads that include error descriptions. | Diff against database contents when troubleshooting missing measurements. |
| `MQTT_raw_input*.json` | MQTT pipeline | Frames exactly as received from the broker. | Detect broker-side schema drift or connectivity hiccups. |
| `MQTT_raw_frames*.json` | MQTT pipeline | Parsed frames grouped before alias routing. | Inspect topic naming and payload segmentation. |
| `MQTT_discard_frames*.json` | MQTT pipeline | Frames rejected by the router. | Quickly surface alias gaps or unexpected payload shapes. |
| `MQTT_Influx*.json` | MQTT pipeline | Ready-to-write points including computed measurement names. | Compare with Influx bucket contents to confirm ingestion succeeded. |

Rotate or archive these files prior to redeployments—the **Log Reset** inject truncates them on each deploy and every 48 hours.

---

## 5. Inspecting structured debug logs

Both the HTTP and MQTT branches persist intermediate states to disk so you can replay the pipeline without live traffic.

1. **Locate the files** – By default they live under `E:\NodeRed\Logs` (Windows) or the directory you configured in each *File out* node. Each stage has a numbered prefix (`01_GET_request.json`, `MQTT_raw_input.json`, etc.).
2. **Tail the latest entries** – On Linux-based deployments:
   ```bash
   sudo tail -f /opt/nodered/logs/01_GET_request.json
   ```
   Pair this with another terminal watching `MQTT_Influx.json` to see the enriched payloads that are handed to the Influx writers.
3. **Replay a single frame** – Use `jq` to inspect a captured message and re-inject it through the flow for debugging:
   ```bash
   jq '.[0]' MQTT_raw_frames.json > /tmp/frame.json
   curl -X POST -H 'Content-Type: application/json' \
     --data @/tmp/frame.json http://localhost:1880/test/replay
   ```
   Create a temporary HTTP-In → Function → Debug chain in Node-RED to capture the output. Remove it after the investigation.
4. **Archive before rotating** – The `Log Reset` inject truncates the files on deploy and every 48 h. Copy files you need to retain into your ticket workspace before redeploying (`cp MQTT_discard_frames.json ~/cases/INC1234/`).


---

## 6. Quick triage: where to enable debug nodes

Use the Node-RED editor’s debug sidebar to stream messages at the key choke points shown below. The diagram references the default group names from the flow JSON.

```text
 MQTT Ingest Group (30ecd298…)
 ├─ All IO-Link topics (mqtt in)
 │    └─ 📌 enable Debug node "MQTT raw tap"
 ├─ IO-Link router (function)
 │    └─ 📌 enable Debug node "Router output"
 └─ Write Influx (influxdb out)
      └─ 📌 enable Debug node "Influx payload"

 HTTP Poll Group (6bd20502…)
 ├─ GET gateway events (http request)
 │    └─ 📌 enable Debug node "HTTP reply"
 └─ Influx data prep (function v8)
      └─ 📌 enable Debug node "HTTP to Influx"
```

> **Tip:** Toggle the small green bug icons on these nodes when triaging issues. Keeping them disabled by default avoids flooding the debug sidebar during normal operation.


---

## 7. Configuration files

| File              | Description                                                                           | Key fields                                                     |
| ----------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `config/masterMap.json`  | Maps IO‑Link JSON properties to short aliases used to build Influx measurement names. | `{ "pins": { "statistics_meanTemperature": "temp_mean", … } }` |
| `config/errorCodes.json` | Dictionary of gateway event codes to human‑readable descriptions.                     | `{ "0x1830": "Secondary supply voltage overrun." }`            |

> **Tip:** Keep these files under version control; the flow loads them at runtime, so changes take effect on next deploy.

### 7.1 Schema-backed editing

- The JSON Schemas in `docs/schemas/` enforce structural correctness. Use `ajv-cli` locally (see [Local validation workflow](../README.md#local-validation-workflow)) to catch typos before deployment.
- When adding a new metric category inside `masterMap.json`, create a sibling object under `pins` with string aliases for every device field you expect. The MQTT router automatically discovers new keys.
- Event code additions in `errorCodes.json` can use either decimal integers (`"6144"`) or hexadecimal strings (`"0x9801"`); the flow normalises both when enriching HTTP events.

### Production overrides

* **Linux edge hosts** – Place the JSON files under a service account directory such as `/opt/nodered/config/` and ensure the account that runs Node-RED can read them (e.g., `chown nodered:nodered /opt/nodered/config && chmod 640`). Update the File In node paths to the Linux location.
* **Container deployments** – Mount production dictionaries into the runtime (for example, bind `/opt/iot/config/` to `/data/config/` so the nodes reference `/data/config/masterMap.json`). When using Kubernetes, place the files in a `ConfigMap` or persistent volume claim and mount them into the Node-RED pod at the same `/data/config/` path.
* **Windows / bare metal** – Place the JSON files in a secured directory outside the repo (such as `D:\NodeRed\config\`). Remember that Windows paths are case-insensitive, so match the Node-RED file paths accordingly.
* **Configuration management** – Treat the `config/` directory as the canonical defaults checked into git; push overrides through CM tooling (Ansible, ConfigMaps, etc.) so flows can pick them up on restart.

### Example mounts and compose snippets

```bash
# Linux bare metal copy
sudo install -o nodered -g nodered -m 0640 config/masterMap.json /opt/nodered/config/masterMap.json
sudo install -o nodered -g nodered -m 0640 config/errorCodes.json /opt/nodered/config/errorCodes.json
```

```yaml
# docker-compose.yml
services:
  nodered:
    image: nodered/node-red:3.1
    user: "1000:1000"           # match host UID/GID that owns /opt/iot/config
    volumes:
      - ./config:/workspace/defaults:ro          # ship repo defaults for reference
      - /opt/iot/config/masterMap.json:/data/config/masterMap.json:ro
      - /opt/iot/config/errorCodes.json:/data/config/errorCodes.json:ro
```

```yaml
# Kubernetes volume mount (Deployment snippet)
volumeMounts:
  - name: flow-config
    mountPath: /data/config
    readOnly: true
volumes:
  - name: flow-config
    configMap:
      name: nodered-flow-config
```

> **Platform notes:**
>
> * Linux paths are case-sensitive—ensure the File In nodes use the exact casing (`masterMap.json` ≠ `MasterMap.json`).
> * When running in containers, match the Node-RED user (`user: "1000:1000"`) to the UID/GID that owns the mounted files, otherwise Node-RED will log permission errors and fall back to defaults.
> * Windows mounts via Docker Desktop translate to `\wsl$` paths—verify the files are shared and readable; long path segments may need quoting in PowerShell imports.

---

## 8. Customisation guide

* **Add devices to polling list** – Edit the `ranges` array in **generate IPs** (supports single host or range).
* **Change poll interval** – Adjust the `repeat` field (seconds) on the HTTP **trigger** inject node.
* **Switch to HTTPS** – Update the `protocol` constant in **build HTTP URL** and import/attach a TLS config node.
* **Edit alias mappings** – Modify `config/masterMap.json` then redeploy.
* **Change identification cadence** – Adjust the `repeat` on the identification **trigger** inject if you need metadata more or less often.
* **Relocate logs** – Update the file paths on the HTTP `01_GET_*` and MQTT `MQTT_*` nodes (ensure the account running Node‑RED has write permission).

---

## 9. Troubleshooting

| Symptom                       | Check                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| No data in Influx             | • Verify InfluxDB credentials and bucket names.<br/>• Confirm MQTT broker is receiving traffic (`mosquitto_sub -t '+/iolink/v1/#'`). |
| `cfg not loaded yet` in debug | Ensure the File In node targets `config/masterMap.json` (or your override) and that the file is valid JSON.                                                                      |
| HTTP polling returns 4xx/5xx  | Check gateway network reachability and authentication requirements.                                                                  |
| File nodes throw `EACCES`     | Update Windows folder permissions or run Node‑RED as administrator.                                                                  |

---

## 10. Deployment & scaling tips

* **Multiple gateways** – MQTT pipeline auto‑scales; for HTTP polling, simply extend the IP list.
* **Kubernetes / Docker** – Mount the `config/` and `logs/` directories as volumes; pass sensitive tokens via secrets.
* **Custom config mounts** – Override the dictionaries by mounting read-only files and updating the File In node paths (e.g., `/data/config/masterMap.json`).
* **High availability** – Consider externalising `errorMap` and `masterMap` into a central git repo or REST endpoint that the flow fetches on start.

---

## License

This project is licensed under the [Apache-2.0](../LICENSE) license.

This repository is managed with the help of AI support and the Codex environment.

