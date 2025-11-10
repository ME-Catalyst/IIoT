import json
from pathlib import Path

FLOW_PATH = Path('src/flows/production/Influx_Data_Pipeline_v1.2.json')
EXPORT_PATH = Path('flows/Influx_Data_Pipeline_v1.2.json')

flow = json.loads(FLOW_PATH.read_text())
node_lookup = {node['id']: node for node in flow}
name_lookup = {nid: (node.get('name') or node.get('label') or node['type']) for nid, node in node_lookup.items()}

def info(*lines: str) -> str:
    return "\n".join(lines)

info_map = {
    'cf2c675f8061347b': info(
        "**Description:** End-to-end IO-Link ingestion pipeline that polls gateways over HTTP, parses MQTT telemetry, and writes structured points into InfluxDB.",
        "**Inputs:** Scheduled inject nodes for HTTP polling, MQTT subscriptions for live traffic, and configuration files loaded on startup.",
        "**Outputs:** Structured measurements routed to InfluxDB plus mirrored debug logs on disk for traceability.",
        "**Usage Notes:** Use the grouped swimlanes to understand responsibilities (HTTP polling, MQTT routing, logging). Update context loaders before deploying new mappings."
    ),
    '726e078392dc6661': info(
        "**Description:** Periodically kicks off the gateway event poller by emitting a blank trigger into *generate IPs*.",
        "**Inputs:** None; fires automatically once five seconds after deploy and every 60 seconds thereafter.",
        "**Outputs:** Sends an empty message to the IP generator so each configured gateway is polled for events.",
        "**Usage Notes:** Adjust the repeat interval to tune HTTP load. Disable when doing manual polling to avoid overlapping requests."
    ),
    '45fe23c1743f8061': info(
        "**Description:** Generates one message per gateway IP for the event polling loop.",
        "**Inputs:** Receives an empty trigger message.",
        "**Outputs:** Emits an array of messages, each carrying an IP in `msg.payload` and `msg.ip`.",
        "**Usage Notes:** Edit the `ranges` array inside the function to add or remove gateways. Use single-host entries for isolated devices."
    ),
    '0273fa386257d86f': info(
        "**Description:** Builds the HTTP URL used to collect gateway event streams.",
        "**Inputs:** Expects `msg.payload` to contain an IPv4 address from the generator.",
        "**Outputs:** Sets `msg.url` with the polling endpoint and forwards the message to the HTTP request node.",
        "**Usage Notes:** Update the base path or protocol in the function body if the gateway firmware changes its API surface."
    ),
    '6d31ed85854d0d21': info(
        "**Description:** Issues the GET request that retrieves `iolink/v1/gateway/events` for each configured gateway.",
        "**Inputs:** Uses `msg.url` from the URL builder; inherits credentials from Node-RED environment if configured.",
        "**Outputs:** Routes the HTTP response to both the enrichment function and the debug serializer.",
        "**Usage Notes:** Configure timeout/retry behaviour in the node settings if gateways are slow to respond."
    ),
    'adee3a7bbf45528f': info(
        "**Description:** Validates HTTP responses and attaches the originating IP for downstream enrichment.",
        "**Inputs:** Receives the raw HTTP response from the request node.",
        "**Outputs:** Passes successful payloads to the array splitter and diverts failures to the logging stream.",
        "**Usage Notes:** Review the function comments for edge-case handling; extend the warning to include more diagnostics if needed."
    ),
    '2ac727f19d830d9e': info(
        "**Description:** Splits the gateway event array into individual messages for granular processing.",
        "**Inputs:** Expects `msg.payload` to be an array of events produced by the gateway.",
        "**Outputs:** Emits one message per event towards the Influx preparation node and the debug serializer.",
        "**Usage Notes:** Adjust the split mode if the gateway schema changes (e.g., switch to streaming)."
    ),
    '07adc65d2bd0b02c': info(
        "**Description:** Persists processed gateway events into InfluxDB (bucket `iot_events`, measurement `gateway_events`).",
        "**Inputs:** Accepts measurement objects produced by *Influx data prep*.",
        "**Outputs:** None within the flow; writes directly to InfluxDB.",
        "**Usage Notes:** Confirm the configured organization, bucket, and precision before deploying to a new environment."
    ),
    '55a97baa1df66b2d': info(
        "**Description:** Bootstraps the flow context with the IO-Link master configuration map.",
        "**Inputs:** Fires once at startup; no external trigger required.",
        "**Outputs:** Passes an empty payload into *Read config JSON* to load `config/masterMap.json`.",
        "**Usage Notes:** Ensure the JSON file exists before deploying or the downstream parser will fail. Re-trigger manually after updating the configuration file."
    ),
    '8c7c9f588c43b1cc': info(
        "**Description:** Reads the IO-Link master configuration JSON from disk.",
        "**Inputs:** Triggered by the startup inject node.",
        "**Outputs:** Emits the file contents as a UTF-8 string to the JSON parser.",
        "**Usage Notes:** Update `config/masterMap.json` to point to new masters; ensure the file path resolves relative to the Node-RED project."
    ),
    'c462826f6ba56b05': info(
        "**Description:** Converts the master configuration JSON string into a JavaScript object.",
        "**Inputs:** Expects `msg.payload` to contain raw JSON text.",
        "**Outputs:** Emits the parsed object to the context storage function.",
        "**Usage Notes:** Leave `property` as `payload` unless upstream nodes change the message shape."
    ),
    '0b8152f986cc3aee': info(
        "**Description:** Caches the parsed master configuration in flow context under `cfg`.",
        "**Inputs:** Receives the parsed configuration object.",
        "**Outputs:** Returns no message; state is stored for later lookups.",
        "**Usage Notes:** Inspect this node if event routing fails—`cfg` must be loaded before MQTT messages arrive."
    ),
    '04eaeab3954ed85b': info(
        "**Description:** Subscribes to all IO-Link MQTT topics published by the gateways.",
        "**Inputs:** No flow input; listens on broker topic `+/iolink/v1/#`.",
        "**Outputs:** Broadcasts each MQTT message to the router, raw-frame logger, and raw-input file sink.",
        "**Usage Notes:** Adjust QoS or topic filter to limit traffic when debugging."
    ),
    '763043855486292d': info(
        "**Description:** Normalizes MQTT frames, applies alias mappings, and routes accepted/discarded payloads.",
        "**Inputs:** Expects structured gateway MQTT messages plus the `cfg` context loaded at startup.",
        "**Outputs:** `0` Influx-ready points, `1` accepted raw frames, `2` discarded frames with reasons.",
        "**Usage Notes:** Review inline comments for guidance when extending supported sections or troubleshooting discards."
    ),
    'bfaa229223513b0a': info(
        "**Description:** Writes processed IO-Link metrics into the `A01` InfluxDB bucket.",
        "**Inputs:** Accepts measurement objects created by the MQTT router.",
        "**Outputs:** None inside the flow; forwards points to InfluxDB.",
        "**Usage Notes:** Ensure the bucket and precision match your InfluxDB organization before deploying."
    ),
    'injectLoad': info(
        "**Description:** Loads the error-code translation table into global context.",
        "**Inputs:** Injects once on deploy and can be manually re-triggered.",
        "**Outputs:** Calls *Read errorCodes.json* so error events can be enriched later.",
        "**Usage Notes:** Re-fire this node whenever `config/errorCodes.json` changes to refresh the in-memory lookup."
    ),
    'readFile': info(
        "**Description:** Reads `config/errorCodes.json` to provide descriptive labels for gateway errors.",
        "**Inputs:** Triggered by the paired inject node.",
        "**Outputs:** Emits the file contents as a string to the JSON parser.",
        "**Usage Notes:** Keep the file path relative to the project so deployments on Linux remain portable."
    ),
    'parseJSON': info(
        "**Description:** Parses the error-code JSON into a JavaScript object.",
        "**Inputs:** Expects raw JSON text in `msg.payload`.",
        "**Outputs:** Passes the parsed lookup table to *Store in global.errorMap*.",
        "**Usage Notes:** Retain the default option of returning objects; the downstream function expects a dictionary."
    ),
    'storeGlobal': info(
        "**Description:** Persists the error-code lookup table in global context for reuse across flows.",
        "**Inputs:** Receives the parsed lookup object.",
        "**Outputs:** Returns no message.",
        "**Usage Notes:** Required for event enrichment; if running in a cluster ensure global context is set to a persistent storage backend."
    ),
    '94c4b64fe48bf7a9': info(
        "**Description:** Starts the identification poller that snapshots static gateway metadata.",
        "**Inputs:** Scheduler fires once after deployment and then every 60 seconds.",
        "**Outputs:** Sends a trigger to the secondary *generate IPs* node feeding the identification HTTP request.",
        "**Usage Notes:** Lengthen the repeat interval if identification rarely changes to reduce unnecessary traffic."
    ),
    '8eaae0548f6f1ac0': info(
        "**Description:** Builds the identification HTTP URL and tags the originating gateway.",
        "**Inputs:** Expects `msg.payload` to be an IPv4 string from the identification IP generator.",
        "**Outputs:** Sets `msg.url` and `msg.gateway` for the GET request node.",
        "**Usage Notes:** Update the path inside the function when firmware revisions relocate identification data."
    ),
    'b9e806b2050cdbc1': info(
        "**Description:** Fetches the gateway identification payload over HTTP.",
        "**Inputs:** Requires `msg.url` from the preceding function.",
        "**Outputs:** Forwards successful responses to the Influx prep function.",
        "**Usage Notes:** Enable TLS or authentication in the node settings if gateways demand secure access."
    ),
    'fdce59a9bc71b2ec': info(
        "**Description:** Visual divider describing the HTTP identification poller lane.",
        "**Inputs:** Documentation node; no runtime inputs.",
        "**Outputs:** None.",
        "**Usage Notes:** Update the text to reflect any architectural changes so the editor stays self-documenting."
    ),
    '4561984a904805be': info(
        "**Description:** Writes gateway identification snapshots to InfluxDB (`gateway_identification` bucket/measurement).",
        "**Inputs:** Receives structured payloads from *All messages to Influx*.",
        "**Outputs:** None within the flow.",
        "**Usage Notes:** Confirm measurement names align with dashboards consuming the data."
    ),
    '64754fb1bd63425a': info(
        "**Description:** Packages the identification response into a single Influx point with gateway metadata.",
        "**Inputs:** Expects the parsed identification JSON and `msg.gateway`.",
        "**Outputs:** Emits a single measurement object for the Influx out node.",
        "**Usage Notes:** Extend the payload mapping when gateways expose additional metadata that should be stored."
    ),
    '43099c37e53f94c1': info(
        "**Description:** Enriches individual gateway events with lookup data and shapes them for InfluxDB.",
        "**Inputs:** Receives one event at a time from the Split node plus `msg.ip`.",
        "**Outputs:** Sends the enriched message to Influx and to the debug serializer.",
        "**Usage Notes:** Review the function comments before changing context keys or topic layout—downstream dashboards rely on the established schema."
    ),
    'cab45e0aedc11ecb': info(
        "**Description:** Editor note identifying the HTTP GET events swimlane.",
        "**Inputs:** None.",
        "**Outputs:** None.",
        "**Usage Notes:** Keep aligned with node grouping when reorganising the canvas."
    ),
    '9d03019ea3347369': info(
        "**Description:** Editor note labelling the MQTT routing swimlane.",
        "**Inputs:** None.",
        "**Outputs:** None.",
        "**Usage Notes:** Update wording if the routing strategy changes significantly."
    ),
    '9b8227a1903ea259': info(
        "**Description:** Serialises accepted MQTT frames for archival logging.",
        "**Inputs:** Receives enriched MQTT messages from the router.",
        "**Outputs:** Emits the same message with `msg.payload` converted to a JSON string.",
        "**Usage Notes:** Paired with the File node targeting `MQTT_raw_frames_v.json`; inspect inline comments for behaviour."
    ),
    '8fa862cf2b5615e5': None,  # file nodes handled later
    '71be59b7c2d5a7bb': None,
    '1f1c7025f2a3ce1c': None,
    '5fbc78e027f42a44': None,
    '17bdca1c684de37f': info(
        "**Description:** Serialises discarded MQTT frames for troubleshooting.",
        "**Inputs:** Receives MQTT messages deemed invalid by the router.",
        "**Outputs:** Emits the same message with `msg.payload` converted to a JSON string.",
        "**Usage Notes:** Check the inline comments for error-handling behaviour; output feeds the discard log files."
    ),
    'ed545088864a6cb0': None,
    '27d6194124762096': None,
    'ea423b52b1e9b387': None,
    '37d1b98dd92fd5d8': None,
    '64b71e04aa8a1a66': None,
    '22361c21b043030f': None,
    'f5ac08b67bcbd3f4': None,
    '818bedb30d9efcc5': None,
    '2cf6872e1b3ad487': info(
        "**Description:** Periodically clears verbose MQTT log files to keep disk usage predictable.",
        "**Inputs:** Fires once at startup and every 172800 seconds (48 hours).",
        "**Outputs:** Sends a timestamp payload to each housekeeping File node configured to delete-and-recreate logs.",
        "**Usage Notes:** Adjust the repeat value to match retention policies. Manual trigger purges logs immediately."
    ),
    'e4624ef9b4a1d94b': info(
        "**Description:** Canvas annotation explaining the MQTT logging and reset utilities.",
        "**Inputs:** None.",
        "**Outputs:** None.",
        "**Usage Notes:** Keep the note updated as logging targets evolve."
    ),
    '4adb3d0d2a6e026e': info(
        "**Description:** Serialises raw MQTT input frames prior to writing them to disk.",
        "**Inputs:** Receives untouched MQTT messages straight from the broker.",
        "**Outputs:** Emits a JSON string in `msg.payload` for the paired File nodes.",
        "**Usage Notes:** Inspect inline comments for edge-case handling when payloads contain non-serialisable values."
    ),
    '00df87db84b78811': None,
    '79356ea0aadc9a91': None,
    '70a12dada24e2da5': None,
    '78b2a95148c008a2': None,
    '68bd7524f18bb41d': info(
        "**Description:** Generates the IP list used by the identification poller.",
        "**Inputs:** Receives a trigger from the scheduled inject node.",
        "**Outputs:** Emits one message per configured IP so the identification HTTP flow can iterate.",
        "**Usage Notes:** Keep the ranges array in sync with the primary poller to avoid uneven coverage."
    ),
    '820eca120de9c8dc': info(
        "**Description:** Serialises HTTP request metadata before it is written to disk for diagnostics.",
        "**Inputs:** Receives the prepared HTTP request message.",
        "**Outputs:** Emits a JSON string in `msg.payload` for the log file.",
        "**Usage Notes:** Inline comments describe the fallback behaviour when serialisation fails."
    ),
    'b580f3c166ef8dda': info(
        "**Description:** Resets the staged HTTP debug logs captured by the GET pipelines.",
        "**Inputs:** Fires on deployment and then every 48 hours.",
        "**Outputs:** Pushes a payload into the GET logging File nodes that are set to delete existing captures.",
        "**Usage Notes:** Trigger manually before a troubleshooting session to start with a clean set of request/response traces."
    ),
    '020cd237371f7f2d': None,
    '88d0db573e750331': None,
    'd6ed388d600d8ec0': None,
    '5228d7f553f62aef': info(
        "**Description:** Serialises HTTP responses before they are persisted for debugging.",
        "**Inputs:** Receives the gateway HTTP response message.",
        "**Outputs:** Emits a JSON string payload for the paired log file.",
        "**Usage Notes:** Refer to inline comments for behaviour when JSON conversion fails."
    ),
    'b773ec8167ad6eac': None,
    'eebe93151283d1c7': info(
        "**Description:** Serialises HTTP tagging payloads for trace logging.",
        "**Inputs:** Receives the message immediately after HTTP responses are tagged.",
        "**Outputs:** Emits the message body as a JSON string.",
        "**Usage Notes:** Inline comments cover error handling to keep logging robust."
    ),
    '7010792667254c11': None,
    '98cb5aedb10e2562': info(
        "**Description:** Serialises split event payloads for chronological logging.",
        "**Inputs:** Receives each event emitted by the Split node.",
        "**Outputs:** Emits a JSON string for the event log files.",
        "**Usage Notes:** Inline comments explain the fallback payload when serialisation fails."
    ),
    '687557aee3e668df': None,
    'b7533422c67034ea': info(
        "**Description:** Serialises enriched events before they are written to Influx-bound debug logs.",
        "**Inputs:** Receives the message immediately after Influx enrichment.",
        "**Outputs:** Emits JSON text for the logging files.",
        "**Usage Notes:** See inline comments for how errors are surfaced to the debug sidebar."
    ),
    '152b94b2cb4c6c3a': None,
    'e34aa1f071f6d44f': None,
    'e2930e5ebe425c46': None,
    'd320d8d3aff09585': None,
    '06c17a95883f1b43': info(
        "**Description:** Annotation describing the HTTP GET logging utilities.",
        "**Inputs:** None.",
        "**Outputs:** None.",
        "**Usage Notes:** Keep wording aligned with the log rotation nodes it references."
    ),
    '3443c80672c5e636': info(
        "**Description:** MQTT subscription that captures every topic on the broker for diagnostic logging.",
        "**Inputs:** No flow input; subscribes to topic `#`.",
        "**Outputs:** Sends frames to the serialiser feeding the catch-all log files.",
        "**Usage Notes:** Disable or narrow the topic filter during production to reduce noise and disk usage."
    ),
    '2bd8aa8546924e19': info(
        "**Description:** MQTT subscription capturing broker control topics for auditing.",
        "**Inputs:** No flow input; listens on `$SYS/#`.",
        "**Outputs:** Routes frames to the serializer for SYS topic logging.",
        "**Usage Notes:** Useful when diagnosing broker health; consider disabling if logs grow too quickly."
    ),
    '2a62ca5551eb6109': info(
        "**Description:** Serialises catch-all MQTT traffic for logging.",
        "**Inputs:** Receives every MQTT message from the `#` subscription.",
        "**Outputs:** Emits JSON text for the wildcard log files.",
        "**Usage Notes:** Inline comments explain the fallback behaviour on serialisation errors."
    ),
    '713a0f9a472d65ca': None,
    'ef8a0a0990524f77': None,
    '13fd02c9973d8e8b': info(
        "**Description:** Serialises broker SYS traffic for archival logging.",
        "**Inputs:** Receives messages from the `$SYS/#` subscription.",
        "**Outputs:** Emits JSON text destined for SYS log files.",
        "**Usage Notes:** Inline comments cover the error handling path to keep logging resilient."
    ),
    '2766c1795827424a': None,
    'e223c50d5c721039': None,
    '23be7c7ce3851001': info(
        "**Description:** Alternate enrichment function for gateway events retained for backwards compatibility.",
        "**Inputs:** Accepts gateway event payloads and uses the global error map.",
        "**Outputs:** Returns the enriched message (no downstream wires at present).",
        "**Usage Notes:** Safe location for staging schema changes before reconnecting to the main pipeline."
    ),
    '2cf6872e1b3ad487': info(
        "**Description:** Periodically clears verbose MQTT log files to keep disk usage predictable.",
        "**Inputs:** Fires once at startup and every 172800 seconds (48 hours).",
        "**Outputs:** Sends a timestamp payload to each housekeeping File node configured to delete-and-recreate logs.",
        "**Usage Notes:** Adjust the repeat value to match retention policies. Manual trigger purges logs immediately."
    ),
    'b580f3c166ef8dda': info(
        "**Description:** Resets the staged HTTP debug logs captured by the GET pipelines.",
        "**Inputs:** Fires on deployment and then every 48 hours.",
        "**Outputs:** Pushes a payload into the GET logging File nodes that are set to delete existing captures.",
        "**Usage Notes:** Trigger manually before a troubleshooting session to start with a clean set of request/response traces."
    ),
    '28500336b4ee8595': info(
        "**Description:** Connection profile for the InfluxDB 2.x instance used by this project.",
        "**Inputs:** None (configuration node).",
        "**Outputs:** Referenced by all Influx-related nodes.",
        "**Usage Notes:** Update host, port, or authentication tokens here when moving between environments."
    ),
    'mqtt-broker-local': info(
        "**Description:** MQTT broker configuration for local development.",
        "**Inputs:** None (configuration node).",
        "**Outputs:** Provides connection details to MQTT In nodes.",
        "**Usage Notes:** Update host/port or credentials before deploying to staged or production brokers."
    )
}

# Ensure log reset inject entries are unique (overwrote duplicates above intentionally)
info_map['2cf6872e1b3ad487'] = info(
    "**Description:** Periodically clears verbose MQTT log files to keep disk usage predictable.",
    "**Inputs:** Fires once at startup and every 172800 seconds (48 hours).",
    "**Outputs:** Sends a timestamp payload to each housekeeping File node configured to delete-and-recreate logs.",
    "**Usage Notes:** Adjust the repeat value to match retention policies. Manual trigger purges logs immediately."
)
info_map['b580f3c166ef8dda'] = info(
    "**Description:** Resets the staged HTTP debug logs captured by the GET pipelines.",
    "**Inputs:** Fires on deployment and then every 48 hours.",
    "**Outputs:** Pushes a payload into the GET logging File nodes that are set to delete existing captures.",
    "**Usage Notes:** Trigger manually before a troubleshooting session to start with a clean set of request/response traces."
)

# Build info strings for file nodes dynamically
for node in flow:
    if node.get('type') == 'file':
        filename = node.get('filename', 'unknown path')
        mode = node.get('overwriteFile')
        if mode == 'delete':
            desc = info(
                f"**Description:** Deletes and recreates `{filename}` when triggered to provide a clean log file.",
                "**Inputs:** Any incoming message (typically from a Log Reset inject) initiates the truncate-and-recreate behaviour.",
                "**Outputs:** None; the node performs a filesystem operation only.",
                "**Usage Notes:** Use before capturing new traces to avoid mixing historical data with current sessions."
            )
        else:
            desc = info(
                f"**Description:** Appends incoming payloads to `{filename}` for historical troubleshooting.",
                "**Inputs:** Expects `msg.payload` to be a JSON string produced by an upstream serializer.",
                "**Outputs:** None; writes directly to disk and does not forward the message.",
                "**Usage Notes:** Paired with a matching delete-mode File node to rotate logs safely."
            )
        info_map[node['id']] = desc

# Provide info for file-in nodes if not already covered (already set above)

# Provide info for JSON serialiser nodes not individually described
serialize_ids = [
    '9b8227a1903ea259', 'b0c120bd5e993542', '17bdca1c684de37f', '4adb3d0d2a6e026e',
    '820eca120de9c8dc', '5228d7f553f62aef', 'eebe93151283d1c7', '98cb5aedb10e2562',
    'b7533422c67034ea', '2a62ca5551eb6109', '13fd02c9973d8e8b'
]
serialize_info = info(
    "**Description:** Serialises the full Node-RED message into a JSON string for downstream file logging.",
    "**Inputs:** Accepts any message object; metadata such as topic and status codes are included in the serialised output.",
    "**Outputs:** Returns the same message with `msg.payload` set to JSON text.",
    "**Usage Notes:** See inline comments for fallback behaviour when the message cannot be stringified."
)
for sid in serialize_ids:
    info_map[sid] = serialize_info

# Function code updates
func_map = {}

common_ip_generator = """/**\n * Build a list of gateway IP addresses for downstream polling.\n * - Supports individual hosts via `host`\n * - Supports numeric ranges via `start` and `end`\n * - Emits one message per IP with both `msg.payload` and `msg.ip` populated\n */\nconst ranges = [\n    { base: '192.168.1', start: 111, end: 130 }\n];\n\n// Guard against a missing configuration so the runtime stays quiet\nif (!Array.isArray(ranges) || ranges.length === 0) {\n    node.warn('No IP ranges configured; skipping poll trigger.');\n    return [[]];\n}\n\nconst ips = []; // collected Node-RED messages\n\nfor (const range of ranges) {\n    // Handle explicit host definitions (single addresses)\n    if (range.host !== undefined) {\n        const ip = `${range.base}.${range.host}`;\n        ips.push({ payload: ip, ip });\n        continue;\n    }\n\n    // Handle numeric ranges; reject malformed values gracefully\n    if (range.start !== undefined && range.end !== undefined) {\n        const start = Number(range.start);\n        const end = Number(range.end);\n        if (Number.isFinite(start) && Number.isFinite(end) && end >= start) {\n            for (let i = start; i <= end; i++) {\n                const ip = `${range.base}.${i}`;\n                ips.push({ payload: ip, ip });\n            }\n        } else {\n            node.warn(`Skipping invalid range definition: ${JSON.stringify(range)}`);\n        }\n        continue;\n    }\n\n    // Anything without host/start/end is ignored but surfaced for debugging\n    node.warn(`Skipping entry without host or range: ${JSON.stringify(range)}`);\n}\n\nif (ips.length === 0) {\n    node.warn('Configured ranges produced no addresses; verify host boundaries.');\n}\n\nreturn [ips];\n"""
func_map['45fe23c1743f8061'] = common_ip_generator
func_map['68bd7524f18bb41d'] = common_ip_generator

func_map['0273fa386257d86f'] = """// Construct the polling URL for gateway events and keep the source IP handy\nconst basePath = '/iolink/v1/gateway/events';\nconst protocol = 'http';\n\n// Normalise the IP string and guard against missing data\nconst ip = (typeof msg.payload === 'string' ? msg.payload : '').trim();\nif (!ip) {\n    node.warn('Missing IP in payload; HTTP request skipped.');\n    return null;\n}\n\n// Warn (but continue) when the payload does not resemble an IPv4 address\nif (!/^\\d{1,3}(\\.\\d{1,3}){3}$/.test(ip)) {\n    node.warn(`IP payload "${ip}" does not look like IPv4; continuing anyway.`);\n}\n\nmsg.url = `${protocol}://${ip}${basePath}`;\nmsg.ip = msg.ip || ip; // ensure downstream nodes can still identify the gateway\n\nreturn msg;\n"""

func_map['adee3a7bbf45528f'] = """// Ensure the response looks healthy before forwarding it downstream\nconst status = Number(msg.statusCode);\nconst hasPayload = msg.payload !== undefined && msg.payload !== null;\n\n// Treat 4xx/5xx responses as failures\nif (Number.isFinite(status) && status >= 400) {\n    node.warn(`HTTP ${status} from ${msg.ip || msg.payload || 'unknown gateway'} – dropping message.`);\n    return null;\n}\n\n// Guard against empty payloads that would break later parsing\nif (!hasPayload) {\n    node.warn(`Empty payload received from ${msg.ip || 'unknown gateway'} – dropping message.`);\n    return null;\n}\n\n// Preserve the originating IP for later enrichment\nmsg.ip = msg.ip || (msg.payload && msg.payload.ip) || null;\n\nreturn msg;\n"""

func_map['0b8152f986cc3aee'] = """// Persist the configuration in flow context so other nodes can reuse it\nconst cfg = msg.payload;\nif (typeof cfg !== 'object' || cfg === null) {\n    node.warn(`Expected configuration object but received ${typeof cfg}.`);\n    return null;\n}\n\nflow.set('cfg', cfg);\nreturn null;\n"""

func_map['storeGlobal'] = """// Persist the error-code map for all flows\nconst errorMap = msg.payload;\nif (typeof errorMap !== 'object' || errorMap === null) {\n    node.warn('Error map payload is not an object; nothing stored.');\n    return null;\n}\n\nif (typeof global.set === 'function') {\n    global.set('errorMap', errorMap);\n} else {\n    // Legacy fallback for very old Node-RED versions\n    context.global = context.global || {};\n    context.global.errorMap = errorMap;\n}\n\nreturn null;\n"""

func_map['8eaae0548f6f1ac0'] = """// Prepare the identification request URL and annotate the message with gateway metadata\nconst basePath = '/iolink/v1/gateway/identification';\nconst ip = (typeof msg.payload === 'string' ? msg.payload : '').trim();\n\nif (!ip) {\n    node.warn('Missing IP in payload; identification request skipped.');\n    return null;\n}\n\nif (!/^\\d{1,3}(\\.\\d{1,3}){3}$/.test(ip)) {\n    node.warn(`Identification IP "${ip}" is not in IPv4 format; continuing anyway.`);\n}\n\nmsg.gateway = ip; // retained for downstream tagging\nmsg.url = `http://${ip}${basePath}`;\n\nreturn msg;\n"""

func_map['64754fb1bd63425a'] = """// Convert the identification payload into a single Influx point\nif (typeof msg.payload !== 'object' || msg.payload === null) {\n    node.warn('Identification payload is not an object; skipping Influx write.');\n    return null;\n}\n\nconst info = msg.payload;\nconst gateway = msg.gateway || 'unknown';\n\nconst point = {\n    measurement: 'device_info',\n    payload: {\n        macAddress:       info.macAddress,\n        serialNumber:     info.serialNumber,\n        productId:        info.productId,\n        vendorName:       info.vendorName,\n        productName:      info.productName,\n        hardwareRevision: info.hardwareRevision,\n        firmwareRevision: info.firmwareRevision,\n        gateway\n    },\n    // Use nanosecond precision to match Influx expectations\n    timestamp: Date.now() * 1e6\n};\n\nreturn [point];\n"""

common_serialize = """// Serialise the complete message for file-based debugging\nlet jsonText;\ntry {\n    jsonText = JSON.stringify(msg);\n} catch (err) {\n    node.warn(`Unable to serialise message: ${err.message}`);\n    jsonText = JSON.stringify({\n        error: err.message,\n        topic: msg.topic,\n        timestamp: new Date().toISOString()\n    });\n}\n\nmsg.payload = jsonText;\nreturn msg;\n"""
for sid in ['9b8227a1903ea259', 'b0c120bd5e993542', '17bdca1c684de37f', '4adb3d0d2a6e026e',
             '820eca120de9c8dc', '5228d7f553f62aef', 'eebe93151283d1c7', '98cb5aedb10e2562',
             'b7533422c67034ea', '2a62ca5551eb6109', '13fd02c9973d8e8b']:
    func_map[sid] = common_serialize

func_map['43099c37e53f94c1'] = """// Enrich an individual gateway event with lookup data for InfluxDB\nconst errorMap = global.get('errorMap') || {};\nconst event = msg.payload;\n\nif (!event || typeof event !== 'object') {\n    node.warn('Event payload missing or not an object; discarding.');\n    return null;\n}\n\nif (!event.origin || !event.message) {\n    node.warn('Event payload missing origin/message metadata; discarding.');\n    return null;\n}\n\nconst masterNumber = Number(event.origin.masterNumber);\nconst portNumber = Number(event.origin.portNumber);\nconst master = Number.isFinite(masterNumber) ? masterNumber : -1;\nconst portTag = Number.isFinite(portNumber) ? `x${Math.max(portNumber - 1, 0)}` : 'xM';\n\nconst code = Number(event.message.code);\nconst hexCode = Number.isFinite(code) ? `0x${code.toString(16).toUpperCase()}` : '0x0';\n\nconst rawMode = (event.message.mode || '').toUpperCase();\nconst eventState = rawMode === 'APPEARS' ? 'event_start'\n  : rawMode === 'DISAPPEARS' ? 'event_stop'\n  : 'unknown';\n\nconst rawDeviceTimestamp = event.time ?? event.timestamp ?? event.timeStamp ?? null;\n\nmsg.topic = `impact67/master/${Number.isFinite(masterNumber) ? masterNumber : 'unknown'}/port/${portTag}`;\nmsg.timestamp = Date.now();\n\nconst description = errorMap[code] || errorMap[hexCode] || 'Unknown code';\n\nmsg.payload = {\n  severity: event.severity,\n  mode: rawMode,\n  eventState,\n  errorCode: Number.isFinite(code) ? code : null,\n  errorCodeHex: hexCode,\n  errorDescription: description,\n  master: masterNumber,\n  port: portTag,\n  isoTime: new Date(msg.timestamp).toISOString(),\n  rawDeviceTimestamp,\n  ip: msg.ip || 'unknown'\n};\n\nreturn msg;\n"""

func_map['23be7c7ce3851001'] = func_map['43099c37e53f94c1']

func_map['5228d7f553f62aef'] = common_serialize
func_map['eebe93151283d1c7'] = common_serialize
func_map['98cb5aedb10e2562'] = common_serialize
func_map['b7533422c67034ea'] = common_serialize
func_map['2a62ca5551eb6109'] = common_serialize
func_map['13fd02c9973d8e8b'] = common_serialize

# Apply updates to flow
for node in flow:
    node_id = node['id']
    if node.get('type') != 'group':
        node['info'] = info_map.get(node_id, info(
            "**Description:** Node description pending.",
            "**Inputs:** See upstream flow for context.",
            "**Outputs:** See downstream flow for context.",
            "**Usage Notes:** Update this note to describe the node's role."
        ))
    if node_id in func_map:
        node['func'] = func_map[node_id]

# Ensure export directory exists
EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Write back to both the source flow and the exported copy
FLOW_PATH.write_text(json.dumps(flow, indent=4))
EXPORT_PATH.write_text(json.dumps(flow, indent=4))
