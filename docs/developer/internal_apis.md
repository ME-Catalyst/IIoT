# Internal APIs and Function References

Although Node-RED flows are composed visually, key logic is implemented with JavaScript function nodes. This reference summariz
es the primary functions and the interfaces they expose.

## Config Loader Functions

* **`loadMasterMap`** – Reads `masterMap.json`, validates required keys (`pins`, `gateways`), and stores the parsed object on the
  flow context as `cfg`.
* **`loadErrorCodes`** – Parses `errorCodes.json` and populates `global.errorMap`. Missing codes trigger warnings logged to the N
ode-RED runtime console.

Both functions accept a single argument, the Node-RED `msg` object, and return it unmodified. Errors throw exceptions that are ca
ught by surrounding `catch` nodes.

## HTTP Event Parser (`Function v8`)

* **Input**: `msg.payload` containing the raw response from `/iolink/v1/gateway/events`.
* **Output**: Array of normalized event objects with keys `gateway`, `port`, `state`, `code`, `timestamp`.
* **Dependencies**: `global.errorMap` and `flow.cfg.pins`.
* **Error Handling**: Throws when context data is missing or when payloads cannot be parsed; the flow routes failures to the str
uctured log branch.

## IO-Link Router (`Function v10`)

* **Input**: MQTT messages under the topic pattern `+/iolink/v1/#`.
* **Output**: Flattened measurement objects ready for InfluxDB writes.
* **Dependencies**: `flow.cfg.pins` to resolve alias maps.
* **Error Handling**: Invalid or unknown measurements are emitted on the secondary output for diagnostics.

## Identification Normalizer

* **Input**: HTTP responses from `/iolink/v1/gateway/identification`.
* **Output**: Simplified metadata objects with device make, model, firmware, and serial number.
* **Dependencies**: None beyond standard Node-RED libraries.

## Shared Utility Functions

Some function nodes reuse helpers stored under `src/lib/`:

| File | Purpose |
| --- | --- |
| `src/lib/context.js` | Safe wrappers for accessing flow and global context with descriptive error messages. |
| `src/lib/normalize.js` | Normalization helpers for timestamps and numerical fields. |
| `src/lib/logging.js` | Appends diagnostic entries to the structured log directory defined by `LOG_DIRECTORY`. |

When updating these utilities, ensure new exports include JSDoc comments and corresponding unit tests under `tests/`.
