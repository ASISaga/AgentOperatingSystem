"""M-1 and M-6 — deliberation assembly (`aos-spec/02-deliberation-orchestration.md`).

The chair is an AGENT, not a selection function: the party choosing who
speaks next reasons over the conversation. That is a decision, not a
mechanism preference, so this module never offers a selection formula as an
alternative — a deliberation whose speaker order is computed is not a
chaired deliberation.

The domain application supplies the roster, which member chairs, and the
numeric configuration; this module wires them into a Group Chat with the
termination condition, the round cap, and per-participant attribution.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, Sequence

from deliberation_kernel.ledger import DeliberationLedger, ProgressLedger

logger = logging.getLogger(__name__)

_LEAD_BID_RE = re.compile(r"LEAD_BID:\s*(.+)", re.I)

#: The chair's standing instruction for the adversarial round (02). At least
#: one round per deliberation MUST invite explicit challenge rather than
#: contribution — this exists because LLM agents converge and agree readily
#: by default, and the rule counteracts that structurally.
ADVERSARIAL_ROUND_PROMPT = (
    "This round is for challenge, not contribution. State what is WRONG with "
    "the emerging position from your own domain: what it costs, what it "
    "assumes without grounding, what it will break. A material objection "
    "MUST NOT be withheld because consensus appears to be forming — the round "
    "budget is a budget, never a licence to suppress dissent."
)


@dataclass(frozen=True)
class Roster:
    """Who is in the room, and which one chairs (02).

    ``agents`` maps a role identifier to whatever object the hosting
    framework accepts as an agent; this mechanism never constructs agents,
    since what an agent IS belongs to the domain application and its
    hosting layer.
    """

    chair: str
    agents: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.chair not in self.agents:
            raise ValueError(f"chair {self.chair!r} is not in the roster")
        if len(self.agents) < 2:
            raise ValueError("a deliberation needs a chair and at least one participant")

    @property
    def participants(self) -> tuple[str, ...]:
        """The roster minus the chair, in the order supplied."""
        return tuple(role for role in self.agents if role != self.chair)

    def require(self, roles: Sequence[str]) -> None:
        missing = [role for role in roles if role not in self.agents]
        if missing:
            raise ValueError(f"roster is incomplete, missing: {missing}")


@dataclass(frozen=True)
class LeadershipBid:
    """A participant's signal that the discussion should pivot to its domain.

    A SIGNAL, never a control transfer (02): the chair reads it as one input
    among others when selecting the next round's speakers. A bid MAY be
    honored, deferred or declined, and declining is not an error and needs
    no justification back to the bidder. Whatever the chair does with a bid,
    only the chair opens, closes, emits the decision record and writes
    shared state — spontaneous leadership governs floor time within a round,
    never write authority.
    """

    role: str
    reason: str


def parse_leadership_bid(text: str, *, role: str = "") -> LeadershipBid | None:
    """Extract an optional ``LEAD_BID:`` signal from a contribution (02)."""
    match = _LEAD_BID_RE.search(text or "")
    if not match:
        return None
    return LeadershipBid(role=role, reason=match.group(1).strip())


@dataclass
class AdversarialObligation:
    """Tracks 02's obligation that one round invite explicit challenge.

    The obligation is on the deliberation, not on any single participant:
    :meth:`due` tells the chair when it can no longer be deferred, and
    :attr:`satisfied` is what a close is checked against (04).
    """

    total_rounds: int
    satisfied: bool = False
    round_held: int | None = None

    def mark_held(self, round_index: int) -> None:
        self.satisfied = True
        self.round_held = round_index

    def due(self, round_index: int) -> bool:
        """True once deferring further would leave the obligation unmet."""
        if self.satisfied:
            return False
        return round_index >= max(self.total_rounds - 1, 0)

    def prompt(self) -> str:
        return ADVERSARIAL_ROUND_PROMPT


def build_group_chat(
    roster: Roster,
    *,
    max_rounds: int,
    termination_condition: Any | None = None,
    intermediate_output_from: str = "all",
    builder_factory: Callable[..., Any] | None = None,
) -> Any:
    """Assemble the Group Chat with the chair as agent-based manager (02).

    ``builder_factory`` exists so the assembly is testable without a live
    orchestration package; it defaults to the real ``GroupChatBuilder``,
    imported lazily so importing this package costs nothing.

    Verified against ``agent-framework-orchestrations`` 1.0.1: the
    agent-based manager is the ``orchestrator_agent`` constructor keyword,
    mutually exclusive with ``selection_func``. ``selection_func`` is
    deliberately never passed — a formula cannot chair a deliberation.
    """
    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1")

    if builder_factory is None:  # pragma: no cover - requires the real package
        from agent_framework_orchestrations import GroupChatBuilder

        builder_factory = GroupChatBuilder

    builder = builder_factory(
        participants=[roster.agents[role] for role in roster.participants],
        orchestrator_agent=roster.agents[roster.chair],
        orchestrator_name=roster.chair,
        intermediate_output_from=intermediate_output_from,
    ).with_max_rounds(max_rounds)

    if termination_condition is not None:
        builder = builder.with_termination_condition(termination_condition)
    return builder.build()


def resolved_or_circling(
    ledger: DeliberationLedger,
    participants: Sequence[str],
    *,
    progress: ProgressLedger | None = None,
    adversarial: AdversarialObligation | None = None,
) -> Callable[[list[Any]], Awaitable[bool]]:
    """Termination condition over the full conversation (02, 04).

    Terminates when the question is resolved or the room is circling. The
    round cap is enforced separately by the round-cap configuration; this
    condition is what stops a deliberation that has already finished, and
    what stops one that is going nowhere. An unmet adversarial obligation
    holds the room open — challenge is not optional because agreement
    arrived early.
    """

    async def _condition(messages: list[Any]) -> bool:
        for message in messages:
            text = getattr(message, "text", None) or str(message)
            author = getattr(message, "author_name", None) or "unknown"
            ledger.observe(author, text)

        ledger_progress = (progress or ProgressLedger()).update(
            ledger, participants=participants
        )
        if adversarial is not None and not adversarial.satisfied:
            return False
        if ledger_progress.circling:
            logger.info("chair detected circling; forcing close (04)")
            return True
        return ledger_progress.resolved

    return _condition


@dataclass
class Deliberation:
    """The per-deliberation state a chair carries: ledgers and obligations."""

    roster: Roster
    max_rounds: int
    ledger: DeliberationLedger = field(default_factory=DeliberationLedger)
    progress: ProgressLedger = field(default_factory=ProgressLedger)
    bids: list[LeadershipBid] = field(default_factory=list)
    adversarial: AdversarialObligation | None = None

    def __post_init__(self) -> None:
        if self.adversarial is None:
            self.adversarial = AdversarialObligation(total_rounds=self.max_rounds)

    def observe(self, role: str, text: str) -> LeadershipBid | None:
        """Fold one contribution into the ledgers; surface any bid (02)."""
        self.ledger.observe(role, text)
        bid = parse_leadership_bid(text, role=role)
        if bid is not None:
            self.bids.append(bid)
        return bid

    def termination_condition(self) -> Callable[[list[Any]], Awaitable[bool]]:
        return resolved_or_circling(
            self.ledger,
            self.roster.participants,
            progress=self.progress,
            adversarial=self.adversarial,
        )

    def build(self, **kwargs: Any) -> Any:
        return build_group_chat(
            self.roster,
            max_rounds=self.max_rounds,
            termination_condition=self.termination_condition(),
            **kwargs,
        )


__all__ = [
    "ADVERSARIAL_ROUND_PROMPT",
    "AdversarialObligation",
    "Deliberation",
    "LeadershipBid",
    "Roster",
    "build_group_chat",
    "parse_leadership_bid",
    "resolved_or_circling",
]
