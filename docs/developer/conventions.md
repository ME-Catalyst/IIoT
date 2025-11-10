# Development Conventions

Adhere to the following conventions when extending the Industrial IoT data pipeline.

## Coding Standards

* **Docstrings** – Provide JSDoc comments for every exported function under `src/`.
* **Formatting** – Run `npm run lint` and `npm run format` before committing code changes.
* **Error Handling** – Throw descriptive `Error` objects that include the gateway ID or topic to accelerate debugging.

## Flow Versioning

* Store production-ready flows under `src/flows/production/` using the naming pattern `Influx_Data_Pipeline_vX.Y.json`.
* Maintain sanitized examples under `examples/flows/` for training and demos.
* Update `CHANGELOG.md` and `docs/architecture/data_flow.md` with behavioral changes.

## Testing

* Execute `python -m tests.validate_flows` to confirm Node-RED exports match the schema expectations.
* Validate configuration dictionaries using the AJV commands described in `docs/user/install_guide.md`.
* Include reproducible steps for any new diagnostics in `docs/troubleshooting/logs_and_diagnostics.md`.

## Documentation

* Keep the root documentation set (`README.md`, `ARCHITECTURE.md`, etc.) synchronized with detailed content under `/docs`.
* Place new diagrams in `docs/visuals/diagrams/` and screenshots in `docs/visuals/screenshots/`.
* Avoid duplicating information across multiple files; link to the authoritative document instead.

## Git Workflow

* Create feature branches per enhancement or bug fix.
* Rebase on the `main` branch before opening a pull request.
* Ensure every commit message follows the format `type(scope): summary` (e.g., `docs(docs): restructure architecture content`).
