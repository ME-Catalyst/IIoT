# Example assets

The `examples/` directory provides sanitized resources that mirror the structure of production artifacts without exposing environment-specific details. Assets are organized by release tag so that operators and developers can rehearse upgrades using the same schema and flow topology shipped in each version.

```
examples/
├── flows/
│   └── v1.2/
│       └── sanitized_data_pipeline_v1.2.json
└── config/
    └── v1.2/
        ├── errorCodes_v1.2.json
        └── masterMap_v1.2.json
```

## Usage
- Import the sanitized flow into a non-production Node-RED instance to review node wiring and context behavior.
- Copy the configuration samples when drafting site-specific overrides, then validate with the JSON schemas in `docs/developer/examples/sample_configs/schemas/` before deployment.
- When a new flow tag is published, add matching folders and filenames under `flows/` and `config/` so the examples remain in lockstep with production exports.
