# Contributing Guide

Thank you for helping improve the Industrial IoT Data Pipeline project. This guide captures the project-specific expectations for exporting Node-RED flows, formatting JSON resources, updating documentation, and validating contributions before review.

## Exporting Node-RED flows

Follow these steps whenever you modify a flow and need to add it to version control:

1. Open the Node-RED editor connected to your development runtime.
2. Deploy your changes to ensure the flow passes the editor's validation checks.
3. From the editor menu choose **Export → Selected flows** (or **Export → All flows** if appropriate).
4. Set the **Export format** to **Formatted JSON** to keep the file readable in Git.
5. Ensure **Indent** is set to **2 spaces** and the **include flow credentials** toggle remains **off**.
6. Replace the corresponding file under [`flows/`](flows/) in this repository with the exported JSON. Use semantic versioning in filenames when creating new revisions (e.g., `Influx_Data_Pipeline_v1.3.json`).
7. Run the validation commands described below to confirm the flow still operates with the shared configuration files.

## JSON formatting standards

Consistent JSON formatting makes diffs easy to review and keeps the automated schema validation effective.

- Use **two spaces** for indentation in all JSON files, including Node-RED flows and configuration dictionaries.
- Ensure files end with a trailing newline and no trailing spaces on any line.
- Sort top-level object keys alphabetically when adding new sections unless a specific order is required by the runtime.
- Prefer double quotes for all string literals (default JSON style) and avoid comments—use documentation files for explanations.
- Use [`npx --yes prettier --write <file>.json`](https://prettier.io/docs/en/cli.html) if you need a formatter. The default Prettier JSON rules match the spacing and newline requirements above.

## Documentation expectations

- Update the [`docs/`](docs/) folder or inline README sections whenever you make changes that affect operator workflows, configuration, or troubleshooting.
- Call out new or updated documentation in your pull request description so reviewers know where to look.
- When adding diagrams, store the source files (e.g., `.drawio`) alongside exported assets (`.png`/`.svg`) so future updates are easy.

## Review checklist

Before requesting a review, complete the following checks and note the results in your pull request:

1. **Schema validation for configuration dictionaries**
   ```bash
   npx --yes ajv-cli validate \
     -s docs/schemas/masterMap.schema.json \
     -d config/masterMap.json

   npx --yes ajv-cli validate \
     -s docs/schemas/errorCodes.schema.json \
     -d config/errorCodes.json
   ```
2. **Flow regression smoke test** – Import the updated flow into a local or staging Node-RED runtime and confirm telemetry arrives in InfluxDB, MQTT subscriptions connect, and the HTTP polling nodes succeed.
3. **Documentation lint** – If you touched Markdown files, run [`npx --yes markdownlint-cli2 README.md docs/**/*.md`](https://github.com/DavidAnson/markdownlint-cli2) or your editor’s Markdown lint integration to catch formatting issues.
4. **Screenshots & diagrams** – Include an updated screenshot of the Node-RED canvas, Grafana dashboard, or other visual surfaces when UI changes are part of the contribution. Attach architecture diagrams when the topology changes.
5. **Changelog note (if applicable)** – Add a bullet to the release notes or deployment runbook if the change impacts operators or rollouts.

## Pull request expectations

- Reference this guide in the pull request template checklist and confirm each item is complete.
- Provide context for reviewers: summarize the problem, outline the solution, and describe any manual validation you performed.
- Attach screenshots or diagrams directly to the pull request or store them under `docs/assets/` and reference them from the description.

We appreciate your help keeping the Industrial IoT Data Pipeline reliable and well-documented!
