## Summary of Changes

<!-- Summarize the Node-RED flow updates and why they are needed. Reference related issues when possible. -->

## Documentation Updates

- [ ] Documentation updated
- [ ] Not required

## Pre-Submission Checks

- [ ] `npx --yes prettier --check "**/*.{json,md}"`
- [ ] `npx --yes ajv-cli validate -s docs/schemas/masterMap.schema.json -d config/masterMap.json`
- [ ] `npx --yes ajv-cli validate -s docs/schemas/errorCodes.schema.json -d config/errorCodes.json`
- [ ] `for file in flows/*.json; do jq empty "$file"; done`
- [ ] `npx --yes markdownlint-cli2 README.md docs/**/*.md CONTRIBUTING.md` *(when Markdown files change)*

<!-- Please ensure you have followed the steps in the [CONTRIBUTING guide](../CONTRIBUTING.md). -->

## Validation Steps

<!-- List the manual or automated checks performed to validate the flows (e.g., deployed to staging, ran specific tests). -->

## Additional Notes

<!-- Add any extra information reviewers should know. -->
