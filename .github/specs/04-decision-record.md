# 04 — DECISION RECORD (generic chair obligations and output shape)

## How a decision is actually reached (organic; the chair reasons, nothing computes)
The chair is the Group Chat manager (02) — an agent-based selector with
access to the full conversation, which already contains every participant's
resonance judgment with its rationale as ordinary messages. There is no
separate step that "feeds scores to the chair"; the chair is in the room
for the whole discussion. The decision is authored, not calculated: the
chair opens, selects speakers each round by reasoning over the room,
detects resolution or circling via a termination condition, and on
termination the framework's completion message — authored by the chair —
IS the decision record.

## The chair's ledger (reasoning discipline, adopted from Magentic's manager
pattern, not its orchestration — Magentic orchestration remains unsuited to
bounded chaired deliberation on cost-predictability grounds; only the
ledger discipline is borrowed)
- **Deliberation ledger** (updated each round): established facts and their
  grounding source, options on the table, open questions, positions and
  resonance judgments per role.
- **Progress ledger** (updated each round): is the question resolved, is
  the room circling the same ground, who should speak next and why.
Circling MUST be detected rather than let burn the round budget: on
detecting it, the chair MUST either force a decision on what is known or
defer the item explicitly (recording a follow-up) — never let a
deliberation quietly exhaust its round cap with nothing decided.

## Chair obligations at close (exhaustive; these are guarantees the chair's
judgment must satisfy, not a rule engine that computes the outcome)
| Condition in the room | The chair MUST |
|---|---|
| a participant scored below 0.2 with `domain_relevance` at or above 0.6 (domain veto) | resolve it (revised proposal, re-scored) or override it explicitly, recording the override and its rationale. Silent override is a defect |
| a participant scored below 0.4 with `domain_relevance` at or above 0.6 | record it as dissent whether or not the decision proceeds |
| every participant's `domain_relevance` below 0.6 | state that the proposal is outside the roster's competence rather than manufacture a judgment |
| high `domain_relevance` but low `confidence` from a participant | seek grounding before closing, or record why closing without it was acceptable |
| the progress ledger shows the room circling | force a decision on what is known, or defer with an explicit follow-up |
| the chair decides against the weight of resonance | say so, and record why |
| the chair closes | MUST record every unresolved oppose/amend position and every material low-resonance objection as dissent. MUST NOT manufacture unanimity by omission. MUST carry forward any new action items into open-follow-up state so the chair's own next opening reviews them — a body that never revisits its own action items has no accountability |
| open follow-ups exist from a prior close | the chair's next opening MUST review those due or overdue, naming the owning participant and asking for status |

## Decision record shape (generic; a domain application's schema is this
shape plus domain-specific fields, never a different shape)
```json
{"$id":"aos.decision.v1","type":"object","additionalProperties":true,
 "required":["decision","rationale","owners","follow_ups","dissent","resonance","purpose_version","model_versions"],
 "properties":{
   "decision":{"type":"string"},
   "rationale":{"type":"string"},
   "owners":{"type":"array","items":{"type":"string"}},
   "follow_ups":{"type":"array","items":{"type":"object","required":["role","action","due"],"properties":{"role":{"type":"string"},"action":{"type":"string"},"due":{"type":"string","format":"date"}}}},
   "dissent":{"type":"array","description":"every unresolved oppose/amend position at close; empty array means genuine unanimity, never omission","items":{"type":"object","required":["role","position","objection"],"properties":{"role":{"type":"string"},"position":{"enum":["oppose","amend"]},"objection":{"type":"string"}}}},
   "resonance":{"type":"array","description":"every participating role's resonance judgment (03); present even when unanimous","items":{"$ref":"aos.resonance.v1"}},
   "overridden_vetoes":{"type":"array","items":{"type":"object","required":["role","override_rationale"],"properties":{"role":{"type":"string"},"override_rationale":{"type":"string"}}}},
   "purpose_version":{"type":"string"},
   "model_versions":{"type":"object","additionalProperties":{"type":"string"}}}}
```
`additionalProperties: true` deliberately, unlike a domain application's own
closed schemas — a domain extends this shape with its own required fields
(e.g. Boardroom's Digest) rather than this mechanism enumerating every
possible domain's fields in advance.
