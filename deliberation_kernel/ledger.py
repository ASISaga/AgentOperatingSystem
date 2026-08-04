"""M-3 (part) — the chair's ledgers (`aos-spec/04-decision-record.md`).

Ledger *discipline* only, adopted from the manager pattern: structured
working memory the chair carries across rounds, so that circling is
detected rather than left to burn the round budget. Nothing here decides
anything — the chair reasons, and these are what it reasons over.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

#: Procedural positions (04). Distinct from a resonance judgment (03):
#: position is what an agent wants to happen next, resonance is how the
#: proposal relates to its purpose. Collapsing the two loses real signal.
POSITIONS: tuple[str, ...] = ("support", "oppose", "amend", "defer")

_POSITION_RE = re.compile(
    r"POSITION:\s*(" + "|".join(POSITIONS) + r")\s*[—\-:]\s*(.+)", re.I
)


def parse_position(text: str) -> tuple[str, str] | None:
    """Extract ``POSITION: <position> — <one line>`` from a contribution."""
    match = _POSITION_RE.search(text or "")
    if not match:
        return None
    return match.group(1).lower(), match.group(2).strip()


@dataclass
class DeliberationLedger:
    """Established facts, options, open questions, positions, resonance (04).

    Updated each round from the conversation the chair can already see; it
    is a reading aid for the chair, never a second source of truth.
    """

    facts: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    positions: dict[str, str] = field(default_factory=dict)
    resonance: dict[str, dict[str, Any]] = field(default_factory=dict)
    round_summaries: list[str] = field(default_factory=list)

    def observe(self, role: str, text: str) -> None:
        position = parse_position(text)
        if position:
            self.positions[role] = position[0]
        self.round_summaries.append(f"{role}: {text[:200]}")

    def record_resonance(self, judgment: Mapping[str, Any]) -> None:
        """Record one participant's judgment, validated on the way in (03)."""
        from deliberation_kernel.resonance import validate_resonance

        validated = validate_resonance(judgment)
        self.resonance[validated["role"]] = validated

    def is_circling(self, *, window: int = 2) -> bool:
        """The room covering the same ground again (04).

        On detecting it the chair MUST force a decision on what is known or
        defer explicitly — never quietly exhaust the round cap.
        """
        if len(self.round_summaries) < window * 2:
            return False
        recent = self.round_summaries[-window:]
        prior = self.round_summaries[-window * 2 : -window]
        return recent == prior

    def unresolved_positions(self) -> dict[str, str]:
        """Roles still holding ``oppose`` or ``amend`` (04, close)."""
        return {
            role: position
            for role, position in self.positions.items()
            if position in ("oppose", "amend")
        }


@dataclass
class ProgressLedger:
    """Is it resolved, is the room circling, who speaks next and why (04)."""

    resolved: bool = False
    circling: bool = False
    next_speakers: tuple[str, ...] = ()
    rationale: str = ""

    def update(
        self,
        ledger: DeliberationLedger,
        *,
        participants: Sequence[str],
        next_speakers: Sequence[str] = (),
        rationale: str = "",
    ) -> "ProgressLedger":
        stated = {role for role in participants if role in ledger.positions}
        self.circling = ledger.is_circling()
        self.resolved = bool(participants) and stated == set(participants) and not any(
            ledger.positions[role] == "amend" for role in stated
        )
        self.next_speakers = tuple(next_speakers)
        self.rationale = rationale
        return self


__all__ = [
    "POSITIONS",
    "DeliberationLedger",
    "ProgressLedger",
    "parse_position",
]
