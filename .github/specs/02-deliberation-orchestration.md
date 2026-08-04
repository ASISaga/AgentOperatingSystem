# 02 — DELIBERATION ORCHESTRATION (generic Group Chat assembly mechanism)

Generalizes what was, at MVP, implemented directly inside Boardroom's
orchestration container. Domain applications instantiate this mechanism by
supplying: a roster of `PurposeDrivenAgent` subclasses, which one is chair,
and configuration values (round bounds, termination criteria specifics).
Nothing here names a business, a company, or any domain-specific role.

## Assembly (Agent Framework Group Chat; chosen over Handoff/Magentic/
Sequential/Concurrent for any chaired, iterative, shared-context deliberation
— rationale is domain-agnostic and belongs here, not repeated per domain)
**The chair is an agent, not a selection function.** Whatever the framework
offers, the party choosing who speaks next MUST be an agent reasoning over
the conversation, not a formula or rotation. This is a decision, not a
mechanism preference: a formula cannot weigh an argument, notice what has
gone unexamined, or recognise urgency in a bid — and a deliberation whose
speaker order is computed is not a chaired deliberation. Participants are
the remaining roster. Which framework constructs express this is the
implementing repository's to determine.

```
chair.open (manager authors first word: agenda, standing decisions, open follow-ups)
  -> round: manager selects next speaker(s) by reasoning over the full
     conversation — arguments, resonance judgments and their rationale (03),
     leadership-bid signals, what remains unexamined
  -> participants contribute (surfaced individually via intermediate_output_from
     -> gives any hosting surface per-participant attribution)
  -> with_termination_condition(full conversation, async): resolved | circling | round cap
  -> on termination the framework emits a completion message AUTHORED BY THE
     MANAGER — that message is the decision record (04); synthesis is the
     native terminal output, not a post-processing step
```
Configuration: `with_max_rounds` enforces the round cap (domain application
sets the actual numbers; this mechanism only enforces whatever is set). The
chair's ledger (04) is the chair's structured working memory across rounds.

## Chair authority (generic rule; domain applications MUST NOT weaken it)
Regardless of which participant leads a given round (spontaneous
leadership, below), only the chair opens, closes, emits the decision record,
and writes shared state. This is unconditional: "spontaneous leadership"
governs floor-time and agenda influence within a round only — never write
authority, never who closes the turn. (Boardroom's specific instantiation:
Founder is chair, unconditionally, for the reasons in Boardroom's own spec.)

## Spontaneous leadership (generic mechanism)
Any participant MAY signal a leadership bid when it judges the discussion
should pivot to its domain urgently. This is a SIGNAL, not a control
transfer: the chair reads it as one input among others (its own agenda
judgment, what remains unexamined, room state) when selecting the next
round's speaker(s). A bid MAY be honored, deferred, or declined; declining
is not an error and needs no justification back to the bidder.

## Adversarial obligation (generic rule)
At least one round per deliberation MUST invite explicit challenge rather
than contribution — the chair asks the roster what is wrong with the
emerging position, not what supports it. Participants MUST NOT withhold a
material objection because consensus appears to be forming; convergence
pressure (round bounds) is a budget constraint, never a licence to suppress
dissent. (This exists because LLM agents converge and agree readily by
default; the rule counteracts that tendency structurally, for any domain.)

## Inbound serialization and mid-turn injection (generic mechanism)
One per-process FIFO with a single consumer, sound because one hosted
session maps to one microVM maps to one process. A message arriving
mid-deliberation MAY be injected into the currently running deliberation as
an additional round input (same identifier, folded as an extra round, never
a silent second deliberation) rather than queued as a separate one — which
case applies is the chair's routing-prompt decision. Full mechanical
definition (this is a total, checkable rule, not a prose permission):
injection keeps the current identifier unchanged; the injected input is
appended to context the chair reads at the next round boundary; the
eventual single decision record reflects both the original trigger and the
injected input. A queued (non-injected) message starts an entirely separate
deliberation with its own identifier once the FIFO reaches it.
