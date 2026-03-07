# Data Model: [FEATURE NAME]

**Feature Number**: [NNN]
**Branch**: [NNN-feature-slug]
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]

---

## Purpose

Define all data entities, their fields, types, and relationships. Every entity must trace back to a user story in `spec.md`. This document is the single source of truth for data shapes used throughout contracts, tests, and implementation.

---

## Entities

### [EntityName]

> Maps to user story: [user story reference from spec.md]

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `id` | `str` | ✅ | Unique identifier | UUID v4 |
| `created_at` | `datetime` | ✅ | Creation timestamp | UTC, ISO 8601 |
| `[field]` | `[type]` | ✅/❌ | [description] | [validation rules] |

**Example**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": "2026-03-07T04:00:00Z"
}
```

---

### [SecondEntityName]

> Maps to user story: [user story reference from spec.md]

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `id` | `str` | ✅ | Unique identifier | UUID v4 |
| `[field]` | `[type]` | ✅/❌ | [description] | [validation rules] |

---

## Relationships

| Entity A | Relationship | Entity B | Cardinality | Notes |
|----------|-------------|----------|-------------|-------|
| [EntityA] | owns | [EntityB] | 1 → N | [notes] |
| [EntityA] | references | [EntityC] | N → 1 | [notes] |

---

## Validation Rules

| Entity | Field | Rule | Error Message |
|--------|-------|------|---------------|
| [Entity] | [field] | [e.g., length ≤ 255] | [e.g., "Name must be ≤ 255 characters"] |

---

## Storage Notes

> Document any Azure or SDK-specific storage considerations.
> Keep implementation choices tied to research.md decisions.

- **Storage backend**: [From research.md choice]
- **Indexing strategy**: [Fields requiring indices for query patterns]
- **Retention policy**: [How long data is kept]

---

## Entity Completeness Checklist

- [ ] Every entity traces to a user story in spec.md
- [ ] All required fields have validation constraints
- [ ] Relationships defined for all foreign references
- [ ] Example JSON provided for each entity
- [ ] No entities added beyond spec requirements (no speculative fields)

→ **Spec**: [NNN-feature-slug/spec.md](spec.md)
→ **Contracts**: [NNN-feature-slug/contracts/](contracts/)
→ **SDD methodology**: `.github/docs/spec-driven.md`
