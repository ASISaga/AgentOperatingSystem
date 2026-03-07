# Research: [FEATURE NAME]

**Feature Number**: [NNN]
**Branch**: [NNN-feature-slug]
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]

---

## Purpose

Capture library choices, performance benchmarks, and technical trade-offs to inform the implementation plan. All choices documented here must link to specific requirements or acceptance criteria.

---

## Library/Framework Options

### [Component or concern]

| Option | Version | Pros | Cons | Recommendation |
|--------|---------|------|------|----------------|
| [Library A] | [x.y.z] | [advantages] | [disadvantages] | ✅ / ❌ |
| [Library B] | [x.y.z] | [advantages] | [disadvantages] | ✅ / ❌ |

**Decision**: [Chosen option and rationale]
**Requirement**: [User story or criterion this serves]

---

## Performance Benchmarks

> Include only benchmarks relevant to the spec's non-functional requirements.

| Scenario | Baseline | Target (from spec) | Measurement Method |
|----------|----------|-------------------|-------------------|
| [e.g., API latency] | [current] | [≤200ms] | [tool/approach] |

---

## Security Considerations

- **Authentication**: [Approach and library]
- **Authorisation**: [RBAC / policy approach]
- **Data protection**: [Encryption at rest / in transit]
- **Input validation**: [Sanitisation approach]
- **Known vulnerabilities**: [Any CVEs in chosen libraries?]

---

## Compatibility and Constraints

> Record any organisational constraints or existing standards that apply.

- **Python version**: [From `.github/specs/repository.md`]
- **Azure Functions SDK**: [From `pyproject.toml`]
- **Deployment target**: [From `azure.yaml`]
- **Existing patterns**: [Patterns from `src/` that must be followed]

---

## Integration Points

| Service/API | Version | Auth Method | Rate Limits | Notes |
|-------------|---------|-------------|-------------|-------|
| [External service] | [API version] | [OAuth / key] | [req/min] | [notes] |

---

## Rejected Options

> Document options considered and rejected, to prevent revisiting them.

| Option | Reason Rejected |
|--------|----------------|
| [Library / approach] | [Why rejected] |

---

## References

- [Link to library documentation]
- [Link to benchmark source]
- [Link to security advisory]
→ **Repository spec**: `.github/specs/repository.md`
→ **SDD methodology**: `.github/docs/spec-driven.md`
