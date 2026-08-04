<!-- REPOSITORY: ASISaga/boardroom-orchestration (path: .github/specs/aos-spec/) -->

# 09 — ASSUMPTIONS AND MECHANISM RECORD (HUMAN REVIEW)

M-1 through M-6 are DONE as mechanism, formalized in place in
`ASISaga/boardroom-orchestration` as the separable top-level package
`deliberation_kernel/`. **Placing it into `ASISaga/agent-operating-system`
is MVP work, in progress** — this is the existing repository, not a fresh
or emptied one (an earlier revision of this file described it as fresh;
that was wrong and is corrected here and in `AA-5`, `AA-6`).

The actual mechanism: `deliberation_kernel` is packaged in
`boardroom-orchestration` as a self-contained directory (not a tag, not a
pip artifact — the directory itself is the deliverable). The Leader
physically moves that directory into `agent-operating-system`, a
cross-repository action neither repository's Coding Agent can perform.
Once there, a receiving Task resolves any filename collisions with what
already exists — per-file, renaming the EXISTING (old) file with a
`-old` suffix, fixing that old file's own internal references so it stays
correct under its new name. Nothing about the old repository's code is
deleted or branched away; it stays present, suffixed where it collided,
untouched where it didn't — readable, disconnected, available for a
post-MVP refactor to actually use (`AA-7`).

Per `a2a/PROTOCOL.md`'s per-repository Coder model, this is TWO Tasks, one
per repository — never one Task spanning both, and never one Coding Agent
expected to act in a repository it isn't running in:
- **In `ASISaga/boardroom-orchestration`** (`0002-package-for-lift-out`):
  package `deliberation_kernel` as a self-contained, liftable directory —
  it already imports nothing from the domain application; confirm that
  holds, produce the directory as the deliverable.
- **In `ASISaga/agent-operating-system`** (`0001-receive-deliberation-kernel`):
  once the Leader has placed the directory, resolve collisions by
  suffixing old files `-old` and fixing their internal references, confirm
  the new mechanism is wired in and reachable, confirm nothing new
  accidentally resolves to an old, suffixed file.

The rows below are kept as the record of WHAT each mechanism is; their
status column now tracks lift-out progress, not a permanent in-place
finding.

## Mechanism record (M-1..M-6: what each is, and its extraction status)
| ID | Mechanism | Spec | Status |
|---|---|---|---|
| M-1 | Group Chat assembly: chair as orchestrator-agent (never a selection function), round cap, termination wiring, per-participant attribution | 02 | Built — `deliberation_kernel/assembly.py`; extraction to `agent-operating-system` MVP, not yet done |
| M-2 | Resonance scoring, anchoring rules, commensurability constraint (cross-role arithmetic structurally refused) | 03 | Built — `deliberation_kernel/resonance.py`; extraction MVP, not yet done |
| M-3 | Chair's ledger, chair obligations at close, generic decision-record shape | 04 | Built — `deliberation_kernel/ledger.py`, `decision.py`; extraction MVP, not yet done |
| M-4 | Domain-attributed memory tagging, dormant role slices, write authority and its one exception | 05 | Built — `deliberation_kernel/memory.py`; extraction MVP, not yet done |
| M-5 | Purpose hierarchy: self-derivation, versioning, stability, roster-change re-derivation | 03 | Built — `deliberation_kernel/purpose.py`; extraction MVP, not yet done |
| M-6 | Spontaneous leadership (leadership-bid signal), adversarial-round obligation | 02 | Built — `deliberation_kernel/assembly.py`; extraction MVP, not yet done |

Boardroom keeps, and does not move: roster
(`MVP_ROSTER`/`CXO_ROLES`/`CHAIR_ROLE`), prompt set and its hashing,
`RoleContext` and company-context injection, and `boardroom.digest.v1`
validation. The kernel imports nothing from the domain application; the
dependency runs one way — that property is exactly what makes the
extraction a packaging change, not a redesign.

**Known not-yet-generalized, recorded rather than half-moved:** 02's
inbound FIFO and mid-turn injection is generic in the spec but was never an
M-row, and currently lives entangled with dedupe markers, identity
verification and mind hydration in the domain application's pipeline. It
was deliberately left in place rather than partially extracted. Whoever
scopes the next Task in that repository decides whether it moves.

## Two separate events, previously conflated
An earlier revision of this section listed six spec sites that "become
FALSE the moment M-1 through M-6 are complete" — treating mechanism
completion and repository relocation as one event. They are two, and only
the first has happened:

**Event 1 — the mechanism is formalized and generic. DONE.** Discharged by
this file's rewritten header and mechanism record above, and by
`00-INDEX.md`'s Status section. Nothing in `boardroom-spec/` is discharged
by this event: that spec set correctly describes Boardroom's own domain
layer, which is unchanged.

**Event 2 — the mechanism lives in a different repository. MVP, IN
PROGRESS** (reopened this revision; a prior revision marked this "NOT
SCHEDULED", before the old `agent-operating-system` was archived and a new
one made the extraction target for MVP). Two Tasks, one per repository
(`AA-5`). The `boardroom-spec/` sites below are consequences of Event 2,
and are touched once it actually completes — not before, and their
completion is not yet claimed just because the event is now scheduled:
- `boardroom-spec/06-agents.md`, the "Two things are true at once" passage.
- `boardroom-spec/16-purpose-and-resonance.md`, the "What is built / What is
  declared" passage.
- `boardroom-spec/17-decision-mechanism.md`, the same passage.
- `boardroom-spec/11-decisions.md`, the "AOS/Boardroom boundary formalized"
  entry — amend its status clause only; decision records are append-only
  history, never rewritten.

Per `a2a/PROTOCOL.md`, a Coding Agent proposes each as a `spec-proposal`
Artifact when the time comes; the Architect applies them. None may be
edited directly.

## Assumptions
| ID | Claim | Blast radius | Discharge |
|---|---|---|---|
| AA-1 | UPDATED (Task 0001's first execution). The mechanisms are extractable without behavior change from wherever they actually live — not confirmed to be Boardroom's own repository; report evidence is `boardroom_core` was split out of `ASISaga/boardroom` (commit `3dc4f86`) and the deliberation code most likely moved with it, into `ASISaga/boardroom-orchestration`, which was unreachable in that Task's execution session. The 154-test figure is unconfirmed against any repository this spec set can currently see | if extraction inadvertently changes behavior, tests may pass against an old path while silently drifting from the new mechanism, or the tests themselves may not exist where assumed | confirm which repository holds the deliberation code and that it is reachable by whichever session executes the next extraction attempt, before treating AA-1 as evaluable at all |
| AA-2 | `agent-operating-system` as a package can depend on `boardroom_core`-shaped generic schemas (04's `aos.decision.v1`, `aos.resonance.v1`) without circularity — i.e. AOS defines the generic shapes and Boardroom's own schemas extend them, not the reverse | if the dependency direction is wrong, Boardroom's schemas would need to exist before AOS's, defeating the reuse purpose | confirm AOS owns `aos.decision.v1`/`aos.resonance.v1` as its own package's schemas at extraction time; Boardroom's Digest/resonance schemas (14, boardroom-spec) become documented extensions, not independent definitions |
| AA-3 | This extraction is genuinely post-MVP, non-blocking work — the MVP ships and runs correctly with these mechanisms living wherever they currently live, independent of this spec set's completeness | none for MVP launch; this is architecture-correctness work for the codebase's long-term shape, not a launch dependency | schedule as a dedicated post-MVP project, not squeezed into ongoing feature work |
| AA-4 | AOS's non-Boardroom reusability is real and not merely aspirational — i.e. there is (or will be) a second, non-business domain application that actually exercises this generic mechanism, validating that it is genuinely domain-agnostic rather than Boardroom's logic with the word "CXO" removed | if no second domain application ever materializes, the generic mechanism's abstractions may be over-fit to Boardroom's specific needs without anyone noticing, since nothing else would exercise them differently | when a second domain application is planned, treat its onboarding onto AOS as the real test of this spec's genericity — expect to find and fix Boardroom-shaped assumptions that leaked into "generic" code |
| AA-5 | RESOLVED with a mechanism, not a repository swap (this revision — corrects the prior "fresh repository" framing, which was wrong). `agent-operating-system` is NOT being replaced by an empty repository; the EXISTING repository receives `deliberation_kernel`'s files directly, in place. Mechanism: `0002-package-for-lift-out` (`boardroom-orchestration`) packages the mechanism as a self-contained directory — the deliverable IS that directory, not a tag or pip artifact. The Leader physically moves it into `agent-operating-system` (a cross-repository action neither Coding Agent can perform). `0001-receive-deliberation-kernel` (`agent-operating-system`) then finds every FILENAME COLLISION between the arrived directory and the existing tree, renames the EXISTING (old) file with a `-old` suffix — never the new one — and fixes every reference/import/invocation inside the OLD codebase's own calling hierarchy that pointed at the renamed file, so the old code stays internally consistent under its new names rather than silently breaking | if collision resolution is done ad hoc rather than as a repeatable process, or if old-code internal references are renamed inconsistently, the old code becomes broken-and-disconnected rather than intact-and-disconnected — losing exactly the "read old and new side by side" value this mechanism exists to preserve | `0001-receive-deliberation-kernel` performs collision resolution via a script or comparable repeatable mechanism (not manual per-file judgment), keeps that mechanism as an Artifact so it's auditable and rerunnable, and its acceptance condition includes: every renamed old file's OWN internal references are fixed, and nothing in the new `deliberation_kernel` code accidentally resolves to an old, suffixed file |
| AA-6 | CORRECTED again (this revision — same "fresh repository" error as AA-5, now fixed consistently). Target is the EXISTING `agent-operating-system` repository, receiving `deliberation_kernel` in place, not a new or emptied repository. Collision risk is real and is the whole point of `AA-5`'s mechanism: any existing file whose name matches something in the arrived `deliberation_kernel` directory gets renamed `-old`, per-file, with its internal references fixed to match. No package/distribution-name decision is needed at the file level — this is a plain directory placement, not a pip install; a package/distribution identity for the whole repository (if wanted) is a separate, later question, not part of this Task | a missed collision silently overwrites or shadows an existing file; an inconsistently-fixed old reference leaves broken old code | `0001-receive-deliberation-kernel`'s collision-resolution mechanism (AA-5) is the discharge; nothing further needed here once that runs cleanly |
| AA-7 | NARROWED again (this revision). Old code is not archived to a branch or deleted — it stays in the repository, suffixed `-old` wherever collision resolution touched it, unsuffixed and simply present wherever it didn't collide. "Hangs around, disconnected" is the correct target state through MVP: present, readable, not wired into anything the new `deliberation_kernel` code calls. Refactoring the OLD code's workflows FORWARD into the new architecture — actually using what's sitting there — remains POST-MVP; this is now the entire remaining scope, narrower than before (MVP already handles getting the old code out of the way cleanly, not just deciding whether to). Whether any old subsystems (`auth/`, `governance/`, `mcp/`, `monitoring/`, `reliability/`, `storage/`, LoRA routing) are worth refactoring forward is not yet decided | if a post-MVP refactor Task finds inconsistently-suffixed or broken old code, the "easier for the Coder" premise of keeping it in place fails — the whole point was old and new being readable side by side, not old code that has bit-rotted from an incomplete rename | when refactoring is prioritized post-MVP, the Leader scopes it against the `-old` codebase as it actually stands (verified working under its suffixed names, per `AA-5`'s acceptance condition), not against a description of the pre-move state |
| AA-8 | The `boardroom-orchestration` repository cannot currently collect its own tests: `boardroom-core` is declared as a bare version specifier (`boardroom-core>=0.1.0,<0.2`) with no index or git source, is not installable, and is not present in the tree; `prompts/{role}.md` is absent though five tests load it; the `Dockerfile` still names pre-split monorepo paths. All pre-existing, none caused by the M-1..M-6 work, and all are consequences of the same incomplete repository split | `AA-1`'s discharge condition (the existing suite passing against code that calls into the mechanism rather than a copy of it) is met STRUCTURALLY — the domain code calls into `deliberation_kernel`, nothing is copied inline — but cannot be DEMONSTRATED by a test run until this resolves. A stub stand-in showed 23/28 passing with all 5 failures on the missing `prompts/`; indicative, not the bar | Architect's answer, supplied: `boardroom-core` resolves as a pip git+tag dependency against its private repository, per `boardroom-spec/20-repository-topology.md` and `10-dependency-lock.md` — exact tag, never a branch, identical pin on every consumer. `prompts/` and the `Dockerfile` paths belonged to the pre-split monorepo layout and did not travel with the code; relocating them is its own Task in `boardroom-orchestration`, not part of M-1..M-6 |
| AA-9 | `deliberation_kernel`'s own 48-test suite (`tests/test_deliberation_kernel.py`, `boardroom-orchestration`) is the only thing that demonstrates the mechanism is domain-agnostic — verified by running it in isolation, repository absent. It stays in `boardroom-orchestration` for now, deliberately not moved during the directory cut-paste: relocating it under `deliberation_kernel/` before `agent-operating-system` has a place for it would silently drop 48 tests from this repository's suite with no replacement. `asyncio_mode = "auto"` (12 of the 48 tests are bare `async def`) travels with the tests, not before | if this Task is treated as "done" once the directory moves, the receiving repository has working mechanism code with zero test coverage proving it, and the sending repository has lost its only proof and not gained a replacement | its own Task, after `0001-receive-deliberation-kernel` lands: move `tests/test_deliberation_kernel.py` into `agent-operating-system`, wire `asyncio_mode = "auto"` (or equivalent) into that repository's own test config, confirm 48/48 pass there before this is closed |