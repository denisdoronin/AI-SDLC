---
name: confluence-integration
description: Rules for reading and writing Confluence pages — where to look for design docs, onboarding, how-tos, how to format new/updated pages. Used by requirements-analyst, architect, docs-writer.
---

# Confluence Integration

## Space structure (example, adapt to the project)
- `Design Docs/` — current architecture, ADRs
- `Onboarding/` — guides for new developers
- `How-To/` — operational instructions (deployment, environment setup, troubleshooting)
- `Meeting Notes/` — do NOT use as a source of requirements (may be outdated)

## Reading
- When looking for context for a task, prioritize: pages explicitly linked to the JIRA epic → `Design Docs` for the relevant component → `How-To`.
- Always check the page's last-updated date — if older than 6 months, mark it as "needs verification" in the output.

## Writing (docs-writer only)
- A new ADR is formatted using the template: Context → Decision → Alternatives → Consequences.
- Updating an existing page — don't rewrite it entirely, make a targeted edit to the section + add a note `Updated: <date>, task <JIRA-KEY>`.
- Never publish a page directly in final status for critical design docs — create it as a draft; a human (Tech Lead) confirms the final publication.

## Forbidden
- Deleting existing pages.
- Changing access rights/space structure.
