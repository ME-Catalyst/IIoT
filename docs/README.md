# Influx Data Pipeline v1.2 – Node‑RED Flow

> **Flow file:** `Influx_Data_Pipeline_v1.2.json`
> **Last reviewed:** 2025‑06‑10

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



---

## 4. Configuration files

| File              | Description                                                                           | Key fields                                                     |
| ----------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `config/masterMap.json`  | Maps IO‑Link JSON properties to short aliases used to build Influx measurement names. | `{ "pins": { "statistics_meanTemperature": "temp_mean", … } }` |
| `config/errorCodes.json` | Dictionary of gateway event codes to human‑readable descriptions.                     | `{ "0x1830": "Secondary supply voltage overrun." }`            |

> **Tip:** Keep these files under version control; the flow loads them at runtime, so changes take effect on next deploy.

### Production overrides

* **Container deployments** – Mount production dictionaries into the runtime (e.g., `/data/config/masterMap.json`) and update the File In node paths to the mounted files.
* **Windows / bare metal** – Place the JSON files in a secured directory outside the repo (such as `D:\NodeRed\config\`) and point the File In nodes at that path.
* **Configuration management** – Treat the `config/` directory as the canonical defaults checked into git; push overrides through CM tooling (Ansible, ConfigMaps, etc.) so flows can pick them up on restart.

---

## 5. Customisation guide

* **Add devices to polling list** – Edit the `ranges` array in **generate IPs** (supports single host or range).
* **Change poll interval** – Adjust the `repeat` field (seconds) on the HTTP **trigger** inject node.
* **Switch to HTTPS** – Update the `protocol` constant in **build HTTP URL** and import/attach a TLS config node.
* **Edit alias mappings** – Modify `config/masterMap.json` then redeploy.
* **Change identification cadence** – Adjust the `repeat` on the identification **trigger** inject if you need metadata more or less often.
* **Relocate logs** – Update the file paths on the HTTP `01_GET_*` and MQTT `MQTT_*` nodes (ensure the account running Node‑RED has write permission).

---

## 6. Troubleshooting

| Symptom                       | Check                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| No data in Influx             | • Verify InfluxDB credentials and bucket names.<br/>• Confirm MQTT broker is receiving traffic (`mosquitto_sub -t '+/iolink/v1/#'`). |
| `cfg not loaded yet` in debug | Ensure the File In node targets `config/masterMap.json` (or your override) and that the file is valid JSON.                                                                      |
| HTTP polling returns 4xx/5xx  | Check gateway network reachability and authentication requirements.                                                                  |
| File nodes throw `EACCES`     | Update Windows folder permissions or run Node‑RED as administrator.                                                                  |

---

## 7. Deployment & scaling tips

* **Multiple gateways** – MQTT pipeline auto‑scales; for HTTP polling, simply extend the IP list.
* **Kubernetes / Docker** – Mount the `config/` and `logs/` directories as volumes; pass sensitive tokens via secrets.
* **Custom config mounts** – Override the dictionaries by mounting read-only files and updating the File In node paths (e.g., `/data/config/masterMap.json`).
* **High availability** – Consider externalising `errorMap` and `masterMap` into a central git repo or REST endpoint that the flow fetches on start.

---

## License

This project is licensed under the [Apache-2.0](../LICENSE) license.

This repository is managed with the help of AI support and the Codex environment.

