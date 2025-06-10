# Influx Data Pipeline v1.0 – Node‑RED Flow

> **Flow file:** `Influx_Data_Pipeline_v1.0.json`
> **Last reviewed:** 2025‑06‑10

This flow ingests IO‑Link gateway data through two independent paths (HTTP polling & MQTT subscribe), enriches it with metadata, writes structured points to InfluxDB 2.x, and archives full frames for audit/debug.  It is designed for **industrial edge deployments** where on‑prem Node‑RED acts as a lightweight collector in a Mosquitto / Influx / Grafana stack.

---

## 1. Quick‑start

| Step                                                              | Action                                                                                                                      |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **1**                                                             | Install **Node‑RED ≥ 3.1** and the palette modules:<br/>`node-red-contrib-influxdb` *(Influx 2.x writer)*                   |
| **2**                                                             | Copy the supporting config files:                                                                                           |
| `E:\NodeRed\Config\masterMap.json` – IO‑Link alias map            |                                                                                                                             |
| `E:\NodeRed\Config\errorCodes.json` – event/error code dictionary |                                                                                                                             |
| **3**                                                             | Import the flow JSON into the Node‑RED editor (`Menu → Import → Clipboard`).                                                |
| **4**                                                             | Double‑click the **InfluxDB** and **Local MQTT** config nodes and enter credentials/hostnames for your environment.         |
| **5**                                                             | Click **Deploy**.  The flow loads its maps, starts polling every 30 s, and begins writing points to the configured buckets. |

---

## 2. High‑level architecture

```text
                +-------------------+
                | masterMap.json    |
                | errorCodes.json   |
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
* **HTTP Poll Pipeline** – Generates IP targets, builds URLs, polls each gateway every 30 seconds, and decodes event arrays.
* **MQTT Ingest Pipeline** – Subscribes to all IO‑Link frames, resolves aliases via `cfg.pins`, and flattens data for storage.
* **InfluxDB Out** – Two writers:

  * `Write Influx` → bucket **A01** (process / diagnostics / statistics / etc.)
  * `write to Influx (gateway_events)` → bucket **iot\_events** (event log)
* **File Logs** – Raw JSON for before/after routing, plus polling diagnostics, written under `E:\NodeRed\Logs`.

---

## 3. Flow tour (node‑by‑node)

### 3.1 Configuration loaders

| Node                                    | Purpose                                                     |
| --------------------------------------- | ----------------------------------------------------------- |
| **Load errorCodes.json** (inject)       | Fires once at boot.                                         |
| **Read errorCodes.json** (file in)      | Reads the dictionary; output is UTF‑8 string.               |
| **Parse to Object** (json)              | Converts to JS object.                                      |
| **Store in global.errorMap** (function) | Saves to global context for later lookup.                   |
| **Load masterMap.json** (inject)        | Similar pattern for gateway pin/metric alias map.           |
| **Read config JSON → parse → save cfg** | Stores to `flow.cfg` so the router can apply field aliases. |

### 3.2 HTTP polling group (`6bd20502…`)

1. **poll every 30 s** *(inject)* – Interval timer (editable).<br>
2. **generate IPs** – Returns one msg per IP as `{ payload:"192.168.1.6", ip:"192.168.1.6" }`. Edit the `ranges` array here to match your LAN.
3. **build HTTP URL** – Appends `/iolink/v1/gateway/events` and stores in `msg.url`.
4. **GET gateway events** *(http request)* – Parses JSON response (via `ret:obj`).  On error, `statusCode` is set and downstream logic drops the message.
5. **tag IP / error handling** – Adds `msg.ip`, filters out 4xx/5xx.
6. **split events array** – Breaks the returned list so each event is processed separately.
7. **decode & tidy** – Normalises fields, maps numeric code → description using `global.errorMap`, and prepares the payload for Influx.
8. **write to Influx (gateway\_events)** – Inserts into **iot\_events** bucket, measurement `gateway_events`.

### 3.3 MQTT ingestion group (`30ecd298…`)

1. **All IO‑Link topics** *(mqtt in)* – Wildcard subscription `+/iolink/v1/#` with QoS 1.
2. **IO‑Link router** – Core logic:

   * Detects section (`processdata`, `diagnostics`, `statistics`, `events`, …).
   * Looks up `aliasMap` from `cfg.pins` and emits one point per mapped field.
   * Events: writes one point per element with severity tag.
   * Output 0 → Influx points; Output 1 → accepted raw; Output 2 → discarded.
3. **Write Influx** – Writes to **A01** bucket using dynamic measurement name `${head}_${portTag}_${alias}`.
4. **Debug file sinks** – Serialise full messages (`JSON.stringify`) and append to

   * `iterative_MQTT_debug_input.json` (pre‑router)
   * `iterative_MQTT_debug_output.json` (post‑router)

### 3.4 Common resources

* **InfluxDB config node** – URL, token, and org must be supplied via the credentials UI or environment variables.
* **Local MQTT broker** – Uses an anonymous connection by default; set username/password as required.

---

## 4. Configuration files

| File              | Description                                                                           | Key fields                                                     |
| ----------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `masterMap.json`  | Maps IO‑Link JSON properties to short aliases used to build Influx measurement names. | `{ "pins": { "statistics_meanTemperature": "temp_mean", … } }` |
| `errorCodes.json` | Dictionary of gateway event codes to human‑readable descriptions.                     | `{ "0x1830": "Secondary supply voltage overrun." }`            |

> **Tip:** Keep these files under version control; the flow loads them at runtime, so changes take effect on next deploy.

---

## 5. Customisation guide

* **Add devices to polling list** – Edit the `ranges` array in **generate IPs** (supports single host or range).
* **Change poll interval** – Adjust the `repeat` field (seconds) on **poll every 30 s**.
* **Switch to HTTPS** – Update the `protocol` constant in **build HTTP URL** and import/attach a TLS config node.
* **Edit alias mappings** – Modify `masterMap.json` then redeploy.
* **Relocate logs** – Change paths in the three **file** nodes (ensure the account running Node‑RED has write permission).

---

## 6. Troubleshooting

| Symptom                       | Check                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| No data in Influx             | • Verify InfluxDB credentials and bucket names.<br/>• Confirm MQTT broker is receiving traffic (`mosquitto_sub -t '+/iolink/v1/#'`). |
| `cfg not loaded yet` in debug | Ensure `masterMap.json` path is correct and file is valid JSON.                                                                      |
| HTTP polling returns 4xx/5xx  | Check gateway network reachability and authentication requirements.                                                                  |
| File nodes throw `EACCES`     | Update Windows folder permissions or run Node‑RED as administrator.                                                                  |

---

## 7. Deployment & scaling tips

* **Multiple gateways** – MQTT pipeline auto‑scales; for HTTP polling, simply extend the IP list.
* **Kubernetes / Docker** – Mount `Config` and `Logs` directories as volumes; pass sensitive tokens via secrets.
* **High availability** – Consider externalising `errorMap` and `masterMap` into a central git repo or REST endpoint that the flow fetches on start.
