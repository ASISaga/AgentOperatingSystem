# Future Roadmap

**Last Updated**: 2026-03-07  
**Audience**: System architects, contributors

Potential future enhancements to the BusinessInfinity repository and agent ecosystem. These are ideas under consideration, not commitments.

## High Priority

- **Additional business workflows** — Expand coverage of C-suite orchestration patterns (e.g., talent management, supply chain optimization, customer success).
- **Workflow test harness** — A more comprehensive mock framework for testing orchestration workflows without hitting live AOS endpoints.
- **Automated spec validation** — CI step that validates spec files in `.github/specs/` for completeness (version header, required sections, no broken references).
- **Agent quality CI gate** — Run `audit-agent-quality.sh` in CI and fail the build if quality metrics drop below thresholds.

## Medium Priority

- **SDD task execution agent** — A coding agent that reads `specs/<NNN>-<slug>/tasks.md` and automatically implements tasks in priority order.
- **Workflow performance tracking** — Track orchestration success rates and latency from workflow invocations.
- **Enterprise capabilities expansion** — Add more MCP server integrations and enterprise workflow patterns.

## Under Consideration

- **Multi-tenant workflows** — Support for tenant-specific orchestration configurations.
- **Workflow versioning** — Support multiple API versions of the same workflow endpoint.
- **Agent capability discovery** — Dynamic agent selection based on declared capabilities rather than static ID lists.

## How to Contribute Ideas

1. Open a GitHub Issue with the `enhancement` label
2. Or use the SDD workflow: `spec-create.prompt.md` to write a spec for the feature
3. Discuss in the PR

→ **SDD workflow**: `.github/specs/spec-driven-development.md`
