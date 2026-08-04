# 05 — MEMORY AND DOMAIN-ATTRIBUTED TAGGING (generic mechanism)

## Per-role memory, seeded ahead of activation
Any role in a domain application's eventual role catalog — not only
currently active roster members — gets its own memory slice from the point
the catalog itself is defined, not only when a participant occupying that
role becomes active. A dormant role's slice is storage only: no running
agent, no model deployment, no purpose of its own while dormant (purpose
derivation happens at role ACTIVATION, per 03, not at catalog definition).
This bounds the standing cost of a large role catalog to storage, not
inference.

## Domain-attributed tagging: one agent wearing multiple hats
When a single active agent's persona covers more than one eventual role's
domain (e.g. a founder-stage single agent covering finance, product, and
technology before dedicated roles exist), that agent's contributions, when
they materially touch a DORMANT role's domain, are tagged and written into
that dormant role's memory slice — not folded anonymously into the acting
agent's own slice alone.

**Mechanism: explicit tagging, not inference.** The acting agent's turn
output is a structured object (native structured-output support, e.g. a
Pydantic model) carrying a `domain_tags: list[role_id]` field alongside its
ordinary contribution. The agent's prompt requires it to name every
dormant-role domain a contribution materially touches; the persist step
writes a summarized, attributed entry into each tagged role's slice IN
ADDITION TO the acting agent's own slice. Explicit tagging is chosen over
inferring domain from content because it is checkable and testable (a
missing or wrong tag is a visible prompt-quality defect) where inference
would fail silently and unauditably.

This is deliberately separate from purpose and resonance (03): an agent
wearing multiple hats still holds ONE purpose and emits ONE resonance
judgment per turn as itself — tagging is a memory-storage attribution
mechanism only, not a multiplication of the agent's identity or scoring.

## Write-authority exception (generic rule)
Write authority is disjoint by construction: each active participant writes
only its own role's slice; the chair additionally writes shared state. ONE
explicit exception: an active agent MAY additionally write to a DORMANT
role's slice via domain-attributed tagging — not a violation of
disjointness, since a dormant role has no active agent to contend with. The
exception ends the moment that role activates (roster change); thereafter
only that role's own agent writes its own slice.

## Consequence: no migration event needed at role activation
When a dormant role later activates, its agent inherits an already-populated
memory slice — no migration, handoff, or cold-start event is needed,
because content was never consolidated into the covering agent's slice
alone in the first place. This is the reason memory bootstrap does not need
its own separate mechanism at roster-change time (contrast: purpose
re-derivation, 03, DOES need an explicit event at that time, because purpose
is a different artifact from memory and was genuinely held by the covering
agent alone until the new role's purpose is derived).
