# 01 — AGENT HIERARCHY

## Chain
```
common infra (python, agent-framework, Foundry Agent Service, shared libs)
  -> PurposeDrivenAgent
    -> LeadershipAgent
      -> BusinessAgent
        -> {domain-specific agent subclasses, e.g. a business's CXO agents}
```
Each layer is both a Python inheritance step AND, in the reference deployment
lineage, a container-image layer (shared base layers deduplicated by the
registry's content-addressable storage — no code duplication across
sibling domain applications that share a common ancestor digest).

## PurposeDrivenAgent (base layer; mechanism owner)
**Repository confirmed**: `ASISaga/purpose-agent` — closing a prior
ambiguity (`a2a/MAP.md` flagged two spellings seen across the
constellation; `purpose-agent` is the live one, stated by the Leader).

**What kind of agent this is, before what it provides**: an abstract base
class for PERPETUAL, purpose-driven agents — they run indefinitely, not to
completion; maintain rich state across every interaction, not a fresh
context per invocation; and work toward a long-term ASSIGNED purpose,
never a short-term task. This is the property everything below follows
from, not a separate detail — the mechanism of purpose-drivenness (below)
only makes sense for an agent that persists long enough for a purpose to
mean something, and the memory/tagging mechanism (05) only makes sense for
an agent whose state accumulates rather than resets.

Provides, for every subclass regardless of domain:
- **mind-server MCP integration**: connection to a domain-agnostic state MCP
  server (the domain application supplies which server, e.g. Boardroom
  supplies mind.asisaga.com; the connection/tool-invocation mechanism itself
  is PurposeDrivenAgent's).
- **The mechanism of purpose-drivenness**: holding a purpose statement,
  self-deriving it from a parent purpose via the agent's own reasoning
  (structured-output invocation, not free text needing parsing), versioning
  it (`purpose_version`/`purpose_hash`), and holding it stable until an
  explicit, discrete re-derivation event (never per-turn drift).
- **What PurposeDrivenAgent does NOT provide**: the actual CONTENT of any
  purpose. "Real purpose is provided by the final agents" (e.g. Boardroom's
  CXOs) — PurposeDrivenAgent supplies the mechanism by which a purpose is
  held, derived, and versioned; the domain application supplies what the
  purpose IS.

## LeadershipAgent / BusinessAgent
Intermediate layers between the domain-agnostic base and a domain's final
agent classes, spread across separately-versioned repositories rather than
held internally by one package — confirmed by report from inside the
repositories (`.gitmodules`, `aos-kernel`'s `pyproject.toml`), which is the
only place these facts were visible.

**Verified relationship (supersedes the earlier UNSPECIFIED/UNCONFIRMED
state of this section):**
- `LeadershipAgent`: own repository, `ASISaga/leadership-agent`. Composed
  into `agent-operating-system` as a git submodule. Depended on by
  `aos-kernel` as a versioned package (`leadership-agent>=1.0.0`). The
  relationship is dependency AND sibling, not internal to either.
- `BusinessAgent`: own repository, `ASISaga/business-agent` — confirmed to
  exist, but notably NOT among `agent-operating-system`'s submodules and
  NOT among `aos-kernel`'s dependencies. Its wiring into the chain this
  file describes is not yet established; do not assume it mirrors
  `LeadershipAgent`'s pattern.
- `PurposeDrivenAgent`: own repository. `agent-operating-system`'s
  submodule list and `aos-kernel`'s dependency list both name it, though
  under two different spellings seen across the constellation
  (`purpose-driven-agent` vs. `purpose-agent`) — which spelling is live is
  unconfirmed (`a2a/MAP.md`).

**Consequence for this file's own chain diagram (above):** the chain
`PurposeDrivenAgent -> LeadershipAgent -> BusinessAgent -> CXO` is not one
package's internal hierarchy. It is at least three separately-versioned
repositories, composed at two different levels (git submodule at the
`agent-operating-system` aggregator; pip dependency at `aos-kernel`), with
`BusinessAgent`'s actual wiring into that composition still unconfirmed.
A change to this chain is a multi-repository release, not an edit.

Regardless of which repository owns them, domain applications depend on
the final subclass only (e.g. Boardroom's CXO agent packages), never by
reaching into these intermediate layers directly — that rule is unaffected
by where the code physically lives.

## Non-goals (explicitly, per the never-compete-with-Foundry mandate)
This layer MUST NOT reimplement anything Foundry Hosted Agents already
provides: session lifecycle, per-caller identity isolation, sandbox hosting,
the Invocations protocol. AOS's agent hierarchy is a composition/behavior
layer ABOVE Foundry, never a substitute for any part of it.