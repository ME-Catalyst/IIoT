# Release Audit Checklist

Use this checklist to satisfy the ME-Catalyst audit controls before tagging or publishing a new release of the Industrial IoT Data Pipeline. Complete every item in order and record the reviewer and date in your release notes.

- [ ] **Documentation updates** – Confirm `README.md`, `docs/architecture/data_flow.md`, `USER_MANUAL.md`, and any operator runbooks reflect the upcoming release behavior. Remove or revise stale references.
- [ ] **Linting and tests** – Run the documented validation workflow (AJV schema checks, flow validators, and automated tests) and capture the command output in the release notes.
- [ ] **MIT license compliance** – Verify `LICENSE.md` still matches the MIT template and that derivative work retains MIT headers where applicable.
- [ ] **Changelog accuracy** – Update `CHANGELOG.md` with release highlights, upgrade guidance, and any known issues. Ensure the entry date matches the tag you will publish.
- [ ] **Maintainer contact review** – Confirm the maintainer or escalation contact details in `README.md` and `CONTRIBUTING.md` remain accurate for this release cycle.
- [ ] **Diagram verification** – Review the architecture and flow diagrams (for example, `ARCHITECTURE.md` and images referenced in `docs/`) to ensure they describe the release accurately.

> **Tip:** Attach the completed checklist (with reviewer initials and completion date) to your GitHub Release notes or internal audit trail for easier traceability.
