# 03 — RESONANCE SCORING (generic proposal-vs-purpose evaluation)

## Purpose hierarchy (generic mechanism)
- **Root purpose** is a first-class, versioned artifact — a durable
  statement of what the top-level entity being served exists to do (a
  domain application supplies WHO authors it and WHEN it may be edited;
  editing is always an explicit, non-silent event, never ambient drift).
- **Each participant's purpose derives from the root purpose at roster
  construction.** Derivation is SELF-derivation, not externally assigned:
  each agent derives its own purpose statement from the root purpose,
  reasoning through its own domain knowledge and persona (01) — not a
  neutral process producing N purposes on the roster's behalf. This is what
  makes participant purposes structurally distinct rather than paraphrases
  of one statement: agents reasoning through different domain lenses are
  forced to diverge, not merely instructed to sound different. Mechanically:
  at roster construction (or role activation on roster change), each agent
  — already holding its domain persona — is invoked once with the root
  purpose as input and its own derived purpose as structured output.
  Derived once, reviewed by whoever owns the root purpose, then STABLE.
- **Stability is load-bearing, not stylistic.** Purpose MUST NOT be
  re-derived per turn or drift as a side effect of deliberation. Resonance
  scores are only comparable across turns if the thing being scored against
  held still. Every purpose change bumps a version marker and is recorded;
  decision records carry a purpose-version reference so a historical score
  stays interpretable against the purpose in force when it was produced.
- **The sole named exception: roster change.** When a roster is
  reconfigured, purpose re-derivation for every AFFECTED agent (not only
  the new one — an existing agent's purpose may narrow as a new participant
  absorbs a domain it previously held alone) is an explicit, discrete,
  auditable event triggered by that change — not a violation of the
  no-per-turn-drift rule, which governs ordinary deliberation, not roster
  administration.

## Resonance scoring
Each participant, on a proposed outcome, emits a resonance judgment: how
strongly the proposal advances its own purpose, produced natively by the
agent's own reasoning as a judgment, not computed by an external scoring
function over embeddings.

```json
{"$id":"aos.resonance.v1","type":"object","additionalProperties":false,
 "required":["role","rationale","score","confidence","domain_relevance"],
 "properties":{
   "role":{"type":"string"},
   "rationale":{"type":"string","description":"MUST be produced BEFORE the score (see anchoring rules)"},
   "score":{"type":"number","minimum":0,"maximum":1},
   "confidence":{"enum":["low","medium","high"]},
   "domain_relevance":{"type":"number","minimum":0,"maximum":1,"description":"how much this proposal falls within this participant's domain at all"}}}
```

### Anchoring rules (normative; these make the score mean something)
The scale MUST be anchored with concrete referents in every role prompt:
- 0.9-1.0 directly advances the core commitment of this participant's purpose
- 0.6-0.8 advances it, with reservations stated in rationale
- 0.4-0.6 orthogonal; neither advances nor undermines
- 0.2-0.4 in tension with the purpose; proceeding has a real cost
- 0.0-0.2 actively undermines the purpose
Rationale MUST precede score. A score without preceding reasoning is a
defect.

### The commensurability constraint (read before implementing aggregation)
Whenever participants infer on different models, resonance scores are NOT
commensurable across roles. Even on a shared model, different personas and
purposes bias scoring, so this rule applies regardless of the inference
setup. Therefore the chair MUST NOT aggregate resonance by arithmetic mean,
weighted average, or any cross-role arithmetic. Scores are valid ordinally
within one role and as threshold signals across roles. Aggregation is
rule-based, not arithmetic — see 04's chair obligations.

### Relationship to procedural position
A resonance judgment and a procedural position (support/oppose/amend/defer,
04) are both emitted and are not redundant: position is procedural, what
the agent wants to happen next; resonance is substantive, how the proposal
relates to purpose. An agent can score high resonance and still hold
position "amend," or score low resonance and hold "defer." Collapsing the
two loses real signal.

### Calibration (ongoing, not one-time)
Because scores drive vetoes (04), drift in a model's scoring behavior is an
integrity risk. A calibration set of known-good and known-bad proposals
MUST be scored per role on every model-version change, with band separation
verified before that version serves traffic. Score distribution per role
SHOULD be monitored continuously.
