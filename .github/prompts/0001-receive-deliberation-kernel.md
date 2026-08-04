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

### Task
`deliberation_kernel/` now sits inside this repository, physically placed
alongside whatever was already here. Your job: make it a correct,
functioning part of this repository — resolving every naming collision
with the existing tree, and confirming the new mechanism is reachable and
usable — without deleting, branching away, or otherwise removing anything
that was already here.

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

### Acceptance conditions (all of these, not just "the collisions are
resolved")
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

### What this Task is explicitly NOT
Not a refactor of any old code — old code gets suffixed and left alone,
not improved, not rewritten, not have its logic touched beyond what the
rename requires. Not a redesign of `deliberation_kernel`'s mechanism —
that's fixed by `aos-spec 01` through `05`; this Task receives and wires
it in, it doesn't change it. Not a decision about whether old subsystems
are worth refactoring forward (`AA-7`) — that's post-MVP and explicitly
not this Task's call.

### Source of truth
`a2a/PROTOCOL.md`'s rule applies: behavior — implementation wins. Target
shape — spec wins. `aos-spec/00-INDEX.md` through `05-memory-and-tagging.md`
is the mechanism spec.

### What comes back
1. This repository's actual starting state (per step zero).
2. The full list of collisions found and resolved, with old/new names.
3. The collision-resolution script or mechanism itself, as an Artifact.
4. Confirmation the acceptance conditions above all hold, or what doesn't.
5. Anything about receiving `deliberation_kernel` that the sending
   repository's Task didn't anticipate.

## History
- state -> submitted, by architect: Task opened.

## Artifacts
(none yet)