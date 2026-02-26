# AOS Kernel Documentation

Documentation for the AOS kernel is distributed within this repository:

- `docs/architecture/` — System architecture
- `docs/development/` — Development guides, contributing
- `docs/getting-started/` — Installation, quickstart
- `docs/specifications/` — Module specifications
- `docs/features/` — Feature documentation
- `docs/reference/` — API reference
- `docs/releases/` — Changelog, release notes

When splitting from the monorepo, copy:
- `docs/architecture/` → here
- `docs/overview/` → here
- `docs/getting-started/` → here (except deployment.md, azure-functions.md)
- `docs/features/` → here
- `docs/reference/` → here
- `docs/specifications/` → here (auth, config, extensibility, governance, mcp, messaging, observability, orchestration, reliability, storage)
- `docs/releases/` → here
- `docs/development/CONTRIBUTING.md` → here
- `docs/development/MIGRATION.md` → here
- `docs/development/REFACTORING.md` → here
