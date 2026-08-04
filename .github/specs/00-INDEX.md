<!-- REPOSITORY: ASISaga/boardroom-orchestration (path: .github/specs/aos-spec/) -->

# AOS SPEC — INDEX

AgentOperatingSystem (package `agent-operating-system`): a domain-agnostic
multi-agent deliberation platform built on Microsoft Agent Framework +
Foundry Agent Service. Provides purpose-driven agent base classes and a
generic chaired-deliberation orchestration mechanism. Never competes with
Foundry's own hosting/session/identity layer — AOS owns composition and
behavior above that layer, not below it.

Mandate (recorded, not to be relitigated without new evidence): keep any
domain application (Boardroom or otherwise) lean — drag-and-drop agent
selection, parameterization, and irreducible domain logic only. Anything
that is a general pattern of purpose-driven multi-agent deliberation belongs
here, not in the domain application.

## A predecessor existed, and has been archived
`agent-operating-system` previously held `aos-kernel` (distribution
`aos-kernel`, import package `AgentOperatingSystem`, v6.0.0), composed
with `leadership-agent`, `purpose-driven-agent`, and five CXO agent repos
as git submodules, shipping `FoundryOrchestrationEngine` — orchestration
built when AOS had to run its own coordination layer, before Foundry
Agent Service existed.

**The direction was settled, not open**: `aos-kernel` predated Foundry and
was the architecture the Foundry pivot already superseded in principle —
02's Group Chat mechanism, running on Foundry Agent Service directly, is
that pivot. **Correction (this revision): there is no separate "archived"
repository and no fresh "new" one.** `agent-operating-system` is the one,
same repository throughout. Its old code (`aos-kernel` and everything
listed above) is being archived IN PLACE — by per-file `-old` suffixing on
naming collision with the arriving mechanism, with the old file's own
internal references fixed to match, not by moving it elsewhere or
replacing the repository.

**MVP places `deliberation_kernel` (`ASISaga/boardroom-orchestration`)
into this repository directly** — this reopens what an earlier revision of
this file closed ("nothing from `aos-kernel` is pulled forward now, MVP
builds entirely in place"). That framing assumed the old code had to be
avoided; the actual mechanism makes avoiding it unnecessary — old and new
coexist, distinguished by the `-old` suffix wherever they'd otherwise
collide. Per `a2a/PROTOCOL.md`'s per-repository Coder model, this is still
two Tasks, one per repository (`AA-5`, 09), with the Leader performing the
one step — the physical cross-repository move — that neither Coding Agent
can. Whether the old, now-suffixed code holds cross-cutting subsystems
worth refactoring forward — auth, governance, observability, storage,
LoRA routing — remains **post-MVP** (`AA-7`, 09), a decision deliberately
deferred, not an open blocker to
this Task.

## Files
01 agent-hierarchy (PurposeDrivenAgent -> BusinessAgent -> LeadershipAgent)
02 deliberation-orchestration (generic Group Chat assembly mechanism)
03 resonance-scoring (generic proposal-vs-purpose evaluation)
04 decision-record (generic Digest-shaped output, dissent, chair obligations)
05 memory-and-tagging (generic domain-attributed memory mechanism)
09 assumptions (HUMAN REVIEW)

## Cross-spec-set reference conventions (binding; both sets number files 01-05/09)
- A BARE file number in this set (e.g. "see 03") always means THIS set's file.
- A reference to Boardroom's spec set is ALWAYS qualified: `boardroom-spec/NN`.
  Never bare.
- Assumption IDs are namespaced: this set uses `AA-n`; Boardroom's uses
  `A-n`. Different series — `AA-1` and `A-1` are unrelated.

## Reader note
This spec follows the same conventions as Boardroom's own spec family
(RFC-2119 normative, closed-world tables, shared-dictionary notation — see
boardroom-spec/METHODOLOGY-AGENT.md, which applies here unchanged). Where a
mechanism specified here is INSTANTIATED by a specific domain application,
that application's own spec (e.g. Boardroom's 06/14/16/17/18/19) states only
the parameters and data it supplies — never re-specifies the mechanism.

## Architect <-> Coding Agent exchange
`a2a/` (this repository) holds the file-based A2A protocol governing spec
proposals and task exchange between the Architect (spec owner) and any
coding agent working across this repository constellation:
`a2a/PROTOCOL.md` (the rules), `a2a/MAP.md` (repository-to-spec ownership,
partially confirmed, gaps marked), `a2a/tasks/` (one file per unit of
work). Read `PROTOCOL.md` before opening or acting on any Task.

## Distribution mechanism
**Corrected against verified fact (previously wrong on every count, written
without checking the repository).** `agent-operating-system` is **public**,
not private — verified via the GitHub API, `"private": false`. It has no
tags to pin. The installable unit is not a package literally named
`agent_operating_system`; it is **`aos-kernel`** (distribution name
`aos-kernel`, currently v6.0.0), one of fifteen git submodules the
`agent-operating-system` repository aggregates.

Until a tag exists for the extracted mechanism's own package (name TBD,
`AA-6`), no consumer can pin a version — this blocks Boardroom's dependency
on it exactly as `AA-2` requires. **Target repository is confirmed:**
`ASISaga/agent-operating-system` itself — M-1..M-6 land alongside
`aos-kernel` and the existing submodule aggregation, not in a new
repository, and not by replacing what's there (`AA-7`). The extracted
mechanism's package name must be chosen to coexist unambiguously with
`aos-dispatcher-azure`/`aos-kernel` in the same source tree.
The private-repository, git+tag pattern that worked for `boardroom_core`
remains the intended mechanism once a real repository, real distribution
name, and a first tag exist; it does not describe today's
`agent-operating-system`.

## Status

**The mechanism this spec set describes now exists as working code.** It
was formalized in place, in `ASISaga/boardroom-orchestration`, as the
separable top-level package `deliberation_kernel/` — one module per
mechanism, importing nothing from the domain application, so the
dependency runs one way. Details and module mapping: `09`.

Two things this Status section previously claimed, both superseded again
this revision — the extraction claim reverses a reversal:
- It said the mechanism is not being extracted, any move is post-MVP.
  **Reopened, and corrected again this revision**: `agent-operating-system`
  is the existing repository, not a new one — old code stays in place,
  archived by per-file `-old` suffix on naming collision, not by being
  moved elsewhere. Placing `deliberation_kernel` into it is MVP work
  (`AA-5`). Not yet done — in progress, as two Tasks, one per repository.
- It cited "154 tests" passing. That figure described a different
  repository's state at a different time and was carried forward
  unverified. What is verified now: `deliberation_kernel`'s own 48 tests
  collect and pass with no domain application present — which is itself
  the evidence the mechanism is separable. The domain application's
  existing suite cannot currently be collected at all (`boardroom-core`
  unresolvable, `prompts/` absent); that is a pre-existing blocker, not
  caused by this work, and is tracked as `AA-8`.

`agent-operating-system`'s old code (`aos-kernel`,
`FoundryOrchestrationEngine`, built before Foundry Agent Service existed)
is being archived IN PLACE, in this same repository — per-file `-old`
suffix on collision with `deliberation_kernel` as it's placed in, with the
old file's internal references fixed to match. No separate archived
repository, no new repository. Refactoring the suffixed old code forward
into active use remains post-MVP (`AA-7`) — it stays present and readable
now, not a present blocker.