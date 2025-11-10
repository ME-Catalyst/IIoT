# Release Procedure

This repository uses date-stamped semantic version tags (for example, `v1.2`) to publish updates to the Industrial IoT Data Pipeline. Follow the steps below whenever preparing a new release. Use the [release audit checklist](AUDIT_CHECKLIST.md) alongside this guide and attach a completed copy to your release notes.

## 1. Prepare the Repository
1. Update [`CHANGELOG.md`](CHANGELOG.md) with the highlights that operators and maintainers should know for the upcoming version.
2. Export the latest Node-RED flow (typically `Influx_Data_Pipeline_vX.Y.json`) and place it under `src/flows/production/` with the correct version suffix. Provide or refresh any redacted companion files under `examples/flows/` for reference deployments.
3. Verify that the default configuration dictionaries remain valid:
   ```bash
   npx --yes ajv-cli validate \
     -s docs/developer/examples/sample_configs/schemas/masterMap.schema.json \
     -d config/masterMap.json

   npx --yes ajv-cli validate \
     -s docs/developer/examples/sample_configs/schemas/errorCodes.schema.json \
     -d config/errorCodes.json
   ```
4. Ensure documentation updates are committed (README, architecture guides, operational notes).
5. Check off each item in the [release audit checklist](AUDIT_CHECKLIST.md) and capture the evidence (command output, reviewer initials) for the release record.

## 2. Tag the Release
1. Bump the version number as needed in the flow filename and documentation.
2. Create an annotated tag following the pattern `vX.Y` (for example, `v1.3`).
   ```bash
   git tag -a v1.3 -m "Industrial IoT Data Pipeline v1.3"
   git push origin v1.3
   ```
3. Confirm the tag points at the commit that contains the updated flow JSON and documentation.

## 3. Publish the GitHub Release
1. Draft a new GitHub Release anchored to the freshly pushed tag.
2. Copy the operator-facing highlights from `CHANGELOG.md` into the release description and add any upgrade guidance or known issues. Mention any licensing or compliance considerations relevant to the release.
3. Attach the exported flow JSON (`src/flows/production/Influx_Data_Pipeline_vX.Y.json`) and any supplementary assets (for example, validation reports, example flows, or dashboard exports) so operators can download the exact artifacts tested for the release.
4. Publish the Release once the assets, notes, and tag alignment have been verified by a second reviewer when possible.

Following this procedure ensures each tag is auditable, that operators can retrieve the correct flow artifacts, and that upgrade expectations remain transparent.
