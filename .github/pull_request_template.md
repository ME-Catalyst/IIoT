## Summary
- [ ] Linked issue: <!-- e.g. Closes #123 -->
- [ ] Summary of changes: <!-- high-level bullet list -->

## Validation
- [ ] `npx --yes ajv-cli validate -s docs/schemas/masterMap.schema.json -d config/masterMap.json`
- [ ] `npx --yes ajv-cli validate -s docs/schemas/errorCodes.schema.json -d config/errorCodes.json`
- [ ] Flow smoke test on Node-RED runtime (describe environment & result)
- [ ] Markdown lint for updated docs (`npx --yes markdownlint-cli2 README.md docs/**/*.md`) or reason it was skipped

## Documentation & visuals
- [ ] Updated relevant docs per [Contributing Guide](../CONTRIBUTING.md)
- [ ] Added/updated screenshots or diagrams when UI or topology changed

## Additional context
- Notes for reviewers:
- Deployment considerations:
