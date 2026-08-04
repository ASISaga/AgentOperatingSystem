"""M-5 — the purpose hierarchy (`aos-spec/03-resonance-scoring.md`).

The mechanism by which a purpose is held, derived and versioned. The
CONTENT of any purpose comes from the domain application (01): this module
never authors a purpose statement, it only makes derivation explicit,
versioned, stable, and re-derived exactly at the one moment the spec allows.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Iterable, Mapping, Sequence


def purpose_version(statement: str, *, root_version: str = "") -> str:
    """A content-addressed version marker for a purpose statement.

    Content addressing rather than a counter: two identical statements
    derived independently are the same purpose, and a historical resonance
    score stays interpretable against the exact text in force when it was
    produced.
    """
    material = f"{root_version}\x00{statement}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


@dataclass(frozen=True)
class Purpose:
    """A held purpose: the statement, its version, and what it derives from."""

    statement: str
    version: str
    derived_from: str = ""

    @classmethod
    def root(cls, statement: str) -> "Purpose":
        return cls(statement=statement, version=purpose_version(statement))

    @classmethod
    def derived(cls, statement: str, *, root: "Purpose") -> "Purpose":
        return cls(
            statement=statement,
            version=purpose_version(statement, root_version=root.version),
            derived_from=root.version,
        )


class PurposeStabilityError(RuntimeError):
    """An attempt to change a purpose outside an explicit, discrete event.

    Stability is load-bearing, not stylistic (03): resonance scores are only
    comparable across turns if the thing being scored against held still.
    """


@dataclass(frozen=True)
class RosterChange:
    """The sole named exception to purpose stability (03).

    ``affected`` is not only the added participant: an existing
    participant's purpose may narrow as a new one absorbs a domain it
    previously held alone. The caller — which knows its own domain — names
    who is affected; this mechanism only guarantees that the re-derivation
    is explicit, discrete and recorded.
    """

    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    affected: tuple[str, ...] = ()
    reason: str = ""

    def to_rederive(self) -> tuple[str, ...]:
        ordered = list(dict.fromkeys([*self.added, *self.affected]))
        return tuple(role for role in ordered if role not in self.removed)


#: How a participant self-derives: given the root purpose statement, the
#: participant's own reasoning returns its own purpose statement. The
#: caller supplies this (a structured-output invocation against the real
#: agent); the mechanism never paraphrases the root purpose on the roster's
#: behalf, which is precisely what would make derived purposes collapse
#: into restatements of one another.
Deriver = Callable[[str, str], Awaitable[str]]


@dataclass
class PurposeHierarchy:
    """Root purpose plus each participant's self-derived purpose (03)."""

    root: Purpose
    purposes: dict[str, Purpose] = field(default_factory=dict)
    events: list[dict[str, str]] = field(default_factory=list)

    async def derive_all(
        self, roles: Sequence[str], deriver: Deriver, *, reason: str = "roster construction"
    ) -> dict[str, Purpose]:
        """Derive a purpose for each role that does not hold one yet."""
        for role in roles:
            if role in self.purposes:
                continue
            await self._derive(role, deriver, reason=reason)
        return dict(self.purposes)

    async def rederive_for_roster_change(
        self, change: RosterChange, deriver: Deriver
    ) -> dict[str, Purpose]:
        """Re-derive every AFFECTED participant's purpose (03's exception).

        Discrete and auditable: every re-derivation appends an event naming
        the roster change that triggered it.
        """
        for role in change.removed:
            if self.purposes.pop(role, None) is not None:
                self.events.append({"role": role, "event": "removed", "reason": change.reason})
        for role in change.to_rederive():
            self.purposes.pop(role, None)
            await self._derive(role, deriver, reason=change.reason or "roster change")
        return dict(self.purposes)

    async def _derive(self, role: str, deriver: Deriver, *, reason: str) -> Purpose:
        statement = await deriver(role, self.root.statement)
        if not (statement or "").strip():
            raise PurposeStabilityError(f"{role} derived an empty purpose")
        purpose = Purpose.derived(statement, root=self.root)
        self.purposes[role] = purpose
        self.events.append(
            {"role": role, "event": "derived", "version": purpose.version, "reason": reason}
        )
        return purpose

    def set_root(self, statement: str, *, reason: str) -> Purpose:
        """Edit the root purpose — always an explicit, non-silent event (03).

        Callers MUST follow this with a re-derivation of every participant:
        derived purposes referencing a superseded root are stale, and this
        is checkable via :meth:`stale_roles`.
        """
        if not (reason or "").strip():
            raise PurposeStabilityError("editing the root purpose requires a stated reason")
        self.root = Purpose.root(statement)
        self.events.append({"role": "", "event": "root-edited", "version": self.root.version, "reason": reason})
        return self.root

    def stale_roles(self) -> tuple[str, ...]:
        """Participants whose purpose derives from a superseded root."""
        return tuple(
            role
            for role, purpose in sorted(self.purposes.items())
            if purpose.derived_from != self.root.version
        )

    def assert_stable(self, role: str, statement: str) -> None:
        """Refuse per-turn drift (03).

        A participant restating its purpose mid-deliberation is drift, not a
        change: it does not become the held purpose, and pretending it does
        would silently invalidate every score compared across turns.
        """
        held = self.purposes.get(role)
        if held is not None and statement.strip() and statement.strip() != held.statement.strip():
            raise PurposeStabilityError(
                f"{role}'s purpose may not change outside a roster-change event (03)"
            )

    def version_marker(self, roles: Iterable[str] | None = None) -> str:
        """The single ``purpose_version`` a decision record carries (04)."""
        selected = sorted(roles) if roles is not None else sorted(self.purposes)
        material = "\x00".join(
            [self.root.version]
            + [f"{role}:{self.purposes[role].version}" for role in selected if role in self.purposes]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def statements(self) -> Mapping[str, str]:
        return {role: purpose.statement for role, purpose in sorted(self.purposes.items())}


__all__ = [
    "Deriver",
    "Purpose",
    "PurposeHierarchy",
    "PurposeStabilityError",
    "RosterChange",
    "purpose_version",
]
