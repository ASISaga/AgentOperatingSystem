---
task_id: 0001-receive-deliberation-kernel
state: submitted
context_id: aos-extraction
from: architect
repository: ASISaga/agent-operating-system
related_tasks: ["ASISaga/boardroom-orchestration#0002-package-for-lift-out"]
---

## Message (role=architect)

Read `copilot-instructions.md` first if this is your first Task in this
repository.

### Step zero: confirm this repository's actual state before anything else
Confirm the Leader has already placed the `deliberation_kernel/` directory
(from `ASISaga/boardroom-orchestration`'s Task `0002-package-for-lift-out`)
into this repository. If it isn't there yet, stop and report — do not
proceed on the assumption it will arrive, and do not fetch or construct it
yourself; this Task begins after the physical move, not before.

Also confirm this repository's actual current content — the Architect has
been told the old `agent-operating-system` (`aos-kernel`, 15-submodule
aggregation) is what's here, but has not independently verified it. Per
`a2a/PROTOCOL.md`'s source-of-truth rule: report what's actually here
before doing anything else, especially if it doesn't match that
description.

### The actual requirement (this revision — corrects a real gap in the
prior version of this Task)
The prior version asked you to place the directory, resolve collisions,
and confirm the mechanism imports. Necessary, not sufficient. This
repository exists so that any `PurposeDrivenAgent`-derived agent can be
composed into a deliberation — that's what `deliberation_kernel` is FOR,
per `aos-spec 01` through `05`. "It imports cleanly" proves the folder
arrived. It does not prove a `PurposeDrivenAgent` can actually be handed
to it and produce a real result. That gap is what this Task now closes.

### Task
Three things, not two:

1. **Place `deliberation_kernel/`** (already here, from
   `boardroom-orchestration`'s `0002-package-for-lift-out`) and resolve
   every naming collision with what already exists, per the rule below.
2. **Confirm every `PurposeDrivenAgent`-derived agent already in this
   repository still works.** This repository already has (or composes,
   via submodule/dependency — `a2a/MAP.md`) `PurposeDrivenAgent`,
   `LeadershipAgent`, and one or more concrete agents built on them. Find
   them. Confirm, concretely — running something, not just reading that
   nothing was deleted — that whatever they could do before this Task
   still works after it. "I didn't touch their files" is not this proof;
   "I ran their existing tests/entry points and they still pass" is.
3. **Prove a `PurposeDrivenAgent`-derived agent can actually reach
   `deliberation_kernel` and get a real result back.** Not an import
   statement in isolation — an actual call: construct or use an existing
   concrete agent, pass it into whatever `deliberation_kernel/assembly.py`
   or the equivalent entrypoint expects as a participant, and show a real
   deliberation round (or the smallest unit of "it worked" the mechanism
   has) actually executing. This is what `deliberation_kernel` is FOR
   (`aos-spec 01`-`05`) — composability with the agent base this
   repository exists to provide — checked, not assumed. Any concrete
   agent already in this repository is a valid choice for the proof; it
   does not need to be a specific one.

If (2) or (3) turns out to be a larger undertaking than this Task should
absorb in one pass — say so plainly, do as much as you genuinely can, and
propose what's left as the next Task with your reasoning. A partial,
honest answer here is worth more than a complete-looking Task that only
checked the folder arrived.

### Dependencies: both optional now, one recommended
`deliberation_kernel` imports `jsonschema` at two call sites
(`resonance.py`, `decision.py`), guarded by `ImportError`. **Superseded
finding, corrected here (this revision): `jsonschema` no longer needs to
be treated as required.** An earlier round found the `ImportError`
fallback checked required-key presence only, silently letting through
judgments `aos.resonance.v1`'s bounds and enums forbid — that gap is
fixed. `deliberation_kernel/schema.py` now enforces the same constraints
without `jsonschema`, verified verdict-for-verdict equivalent across 16
test instances and by an independent re-run with `jsonschema` blocked
(56/56 passing). Installing `jsonschema` is still RECOMMENDED — better
error messages, full JSON Schema semantics where the fallback covers a
narrower keyword set — but it is genuinely optional for spec-conformant
behavior, same as `agent_framework_orchestrations` (also confirmed
optional, blocked with no test failure).

### The collision-resolution rule (exact, not a judgment call)
For every file in the arrived `deliberation_kernel/` directory whose name
collides with an existing file elsewhere in this repository:
1. Rename the EXISTING (old) file by appending `-old` before its
   extension (e.g. `assembly.py` -> `assembly-old.py`). Never rename or
   suffix the new file — the new code keeps its plain names.
2. Find every reference to that old file WITHIN THE OLD CODEBASE'S OWN
   CALLING HIERARCHY — imports, invocations, path references, anything
   that would break because the file's name changed — and fix each one to
   point at the renamed file. The old code must remain internally
   consistent and (as far as this Task can determine) working under its
   new names, not just present.
3. Do this via a script or other repeatable, rerunnable mechanism — not
   manual, ad hoc, per-file edits. Keep that script as an Artifact: it
   should be possible to see exactly what it did and run it again if
   something was missed.
4. Where no collision exists, touch nothing. Old files that don't collide
   stay exactly as they are, unsuffixed, simply present.

### Acceptance conditions (all of these — the first four check the folder
arrived correctly; the last two check what this repository actually exists
to guarantee, and are the point of this Task, not an afterthought)
- Every filename collision is resolved per the rule above.
- Every old file's own internal references are fixed to match its new
  name — check this by tracing the calling hierarchy, not by assuming the
  script got every reference.
- Nothing in the new `deliberation_kernel` code accidentally resolves to
  an old, `-old`-suffixed file (a stale import that happens to still
  work because it's pointing at the wrong thing would be worse than an
  import that fails loudly).
- The new mechanism's public API (per
  `report-01-mechanism-formalized.md`'s module table — `assembly.py`,
  `resonance.py`, `ledger.py`, `decision.py`, `memory.py`, `purpose.py`)
  is reachable and importable from this repository as it now stands.
- **Every `PurposeDrivenAgent`-derived agent already in this repository's
  own tests or entry points still run and pass after this Task**, not
  merely "still present in the tree."
- **A real, executed proof exists that a concrete `PurposeDrivenAgent`-
  derived agent can be handed to `deliberation_kernel`'s mechanism and
  produce a genuine result** — the composability this repository exists
  to provide, checked, not assumed.

### What this Task is explicitly NOT
Not a refactor of any old code — old code gets suffixed and left alone,
not improved, not rewritten, not have its logic touched beyond what the
rename requires. Not a redesign of `deliberation_kernel`'s mechanism —
that's fixed by `aos-spec 01` through `05`; this Task receives and wires
it in, it doesn't change it. Not a decision about whether old subsystems
are worth refactoring forward (`AA-7`) — that's post-MVP and explicitly
not this Task's call.

**Not making `deliberation_kernel` the default entry point for
`PurposeDrivenAgent`-derived agents generally.** Proving a concrete agent
CAN reach the mechanism (above) is a demonstration, one real example, on a
path you construct for the proof. Deciding that this becomes THE way every
agent in this repository engages with deliberation going forward — the
actual wiring-as-default decision — is separate, and belongs to whoever
next scopes that as its own Task once this one confirms composability
holds at all.

### Source of truth
`a2a/PROTOCOL.md`'s rule applies: behavior — implementation wins. Target
shape — spec wins. `aos-spec/00-INDEX.md` through `05-memory-and-tagging.md` — now physically
in THIS repository (`.github/specs/aos-spec/`, per `a2a/MAP.md`), not an
external citation — is the mechanism spec.

### What comes back
1. This repository's actual starting state (per step zero).
2. The full list of collisions found and resolved, with old/new names.
3. The collision-resolution script or mechanism itself, as an Artifact.
4. Confirmation the acceptance conditions above all hold, or what doesn't.
5. Anything about receiving `deliberation_kernel` that the sending
   repository's Task didn't anticipate.

## History
- state -> submitted (unchanged), by architect: Corrected following the
  Leader's move of `deliberation_kernel`/`aos-spec` into this repository.
  Two citation errors fixed: `aos-spec` is now cited as physically local
  (`.github/specs/aos-spec/`), not an external reference; the module-table
  citation to `report-01-mechanism-formalized.md` (which lives in
  `boardroom-orchestration`'s own artifacts, not accessible here) replaced
  with a direct pointer to the code itself. File relocated to this
  repository's own `a2a/tasks/`, where it should have lived from the
  start rather than in the separate spec-drafting tree it was authored in.
- state -> submitted (unchanged), by architect: Task rewritten to state
  what this repository needs to guarantee in its own terms — composability
  between `PurposeDrivenAgent`-derived agents and `deliberation_kernel` —
  rather than a downstream product's requirement stated verbatim. "Resolve
  collisions and confirm it imports" proved the folder arrived, not that
  composability holds. Added: confirm every agent already here still
  works, and a real executed proof that a concrete agent can reach
  `deliberation_kernel` and get a genuine result. Explicitly NOT included:
  wiring this as the default entry point generally — that's a separate,
  later Task.
- state -> submitted, by architect: Task opened.

## Artifacts
(none yet)
