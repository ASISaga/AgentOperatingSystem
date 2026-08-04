"""``deliberation_kernel`` — the generic chaired-deliberation mechanism.

This package is the formalization of `aos-spec/00-INDEX.md` through
`aos-spec/05-memory-and-tagging.md` as working code, in place, in this
repository. It is domain-agnostic by construction: nothing here names a
business, a company, a CXO role, a roster member, a connector, a BizEvent,
or any other Boardroom concept, and it imports nothing from
``boardroom_core`` or ``boardroom_orchestration``. The dependency direction
is one-way — the domain application depends on the kernel, never the
reverse — so a future move of this package into its own repository is a
repository change, not a redesign.

Mechanism map (`aos-spec/09-assumptions.md` migration table, read as WHAT
must exist here):

| ID  | Mechanism                                              | Module                  |
|-----|--------------------------------------------------------|-------------------------|
| M-1 | Group Chat assembly, termination wiring, round cap      | ``assembly``            |
| M-2 | Resonance scoring, anchoring, commensurability          | ``resonance``           |
| M-3 | Chair's ledger, obligations, decision-record shape      | ``ledger``/``decision`` |
| M-4 | Domain-attributed memory tagging                        | ``memory``              |
| M-5 | Purpose hierarchy (self-derivation, stability)          | ``purpose``             |
| M-6 | Spontaneous leadership, adversarial-round obligation    | ``assembly``            |

What a domain application supplies (and this package never contains): the
roster of agents and which one chairs, the content of any purpose, the
numeric configuration values, the role catalog, prompt text, and any
domain-specific fields it adds to the decision record.
"""

from deliberation_kernel.assembly import (
    AdversarialObligation,
    Deliberation,
    LeadershipBid,
    Roster,
    build_group_chat,
    parse_leadership_bid,
    resolved_or_circling,
)
from deliberation_kernel.decision import (
    DECISION_SCHEMA,
    DECISION_SCHEMA_ID,
    POSITIONS,
    DecisionError,
    ObligationBreach,
    unmet_chair_obligations,
    validate_decision,
)
from deliberation_kernel.ledger import DeliberationLedger, ProgressLedger, parse_position
from deliberation_kernel.memory import (
    RoleCatalog,
    TaggedContribution,
    WriteAuthorityError,
    attributed_writes,
    check_write_authority,
    seed_slices,
)
from deliberation_kernel.purpose import (
    Purpose,
    PurposeHierarchy,
    PurposeStabilityError,
    RosterChange,
    purpose_version,
)
from deliberation_kernel.resonance import (
    ANCHOR_PROMPT_BLOCK,
    RESONANCE_SCHEMA,
    RESONANCE_SCHEMA_ID,
    CommensurabilityError,
    ResonanceError,
    is_domain_veto,
    is_recordable_dissent,
    needs_grounding,
    outside_roster_competence,
    validate_resonance,
)

__all__ = [
    "ANCHOR_PROMPT_BLOCK",
    "AdversarialObligation",
    "CommensurabilityError",
    "DECISION_SCHEMA",
    "DECISION_SCHEMA_ID",
    "DecisionError",
    "Deliberation",
    "DeliberationLedger",
    "LeadershipBid",
    "ObligationBreach",
    "POSITIONS",
    "ProgressLedger",
    "Purpose",
    "PurposeHierarchy",
    "PurposeStabilityError",
    "RESONANCE_SCHEMA",
    "RESONANCE_SCHEMA_ID",
    "ResonanceError",
    "RoleCatalog",
    "Roster",
    "RosterChange",
    "TaggedContribution",
    "WriteAuthorityError",
    "attributed_writes",
    "build_group_chat",
    "check_write_authority",
    "is_domain_veto",
    "is_recordable_dissent",
    "needs_grounding",
    "outside_roster_competence",
    "parse_leadership_bid",
    "parse_position",
    "purpose_version",
    "resolved_or_circling",
    "seed_slices",
    "unmet_chair_obligations",
    "validate_decision",
]
