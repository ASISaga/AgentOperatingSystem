"""M-3 — decision-record shape and chair obligations at close.

`aos-spec/04-decision-record.md`. The decision is authored by the chair,
never calculated: this module holds the SHAPE the chair's close must take
and a checkable statement of the obligations that close must satisfy. A
breach reported here is a defect in the close, not a veto over it — the
chair decides, the mechanism refuses to let a guarantee be skipped
silently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from deliberation_kernel.ledger import POSITIONS, DeliberationLedger
from deliberation_kernel.resonance import (
    RESONANCE_SCHEMA,
    RESONANCE_SCHEMA_ID,
    is_domain_veto,
    is_recordable_dissent,
    needs_grounding,
    outside_roster_competence,
)
from deliberation_kernel.schema import first_error

DECISION_SCHEMA_ID = "aos.decision.v1"

#: ``additionalProperties: true`` deliberately (04): a domain application
#: extends this shape with its own required fields rather than this
#: mechanism enumerating every possible domain's fields in advance.
DECISION_SCHEMA: dict[str, Any] = {
    "$id": DECISION_SCHEMA_ID,
    "type": "object",
    "additionalProperties": True,
    "required": [
        "decision",
        "rationale",
        "owners",
        "follow_ups",
        "dissent",
        "resonance",
        "purpose_version",
        "model_versions",
    ],
    "properties": {
        "decision": {"type": "string"},
        "rationale": {"type": "string"},
        "owners": {"type": "array", "items": {"type": "string"}},
        "follow_ups": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["role", "action", "due"],
                "properties": {
                    "role": {"type": "string"},
                    "action": {"type": "string"},
                    "due": {"type": "string", "format": "date"},
                },
            },
        },
        "dissent": {
            "type": "array",
            "description": (
                "every unresolved oppose/amend position at close; empty array "
                "means genuine unanimity, never omission"
            ),
            "items": {
                "type": "object",
                "required": ["role", "position", "objection"],
                "properties": {
                    "role": {"type": "string"},
                    "position": {"enum": ["oppose", "amend"]},
                    "objection": {"type": "string"},
                },
            },
        },
        # 04 writes this as {"$ref": "aos.resonance.v1"}; a bare $id is not a
        # resolvable reference without a registry, so the resonance schema is
        # resolved here at definition time. Same shape, one source (03).
        "resonance": {
            "type": "array",
            "description": (
                "every participating role's resonance judgment (03); present "
                "even when unanimous"
            ),
            "items": RESONANCE_SCHEMA,
        },
        "overridden_vetoes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["role", "override_rationale"],
                "properties": {
                    "role": {"type": "string"},
                    "override_rationale": {"type": "string"},
                },
            },
        },
        "purpose_version": {"type": "string"},
        "model_versions": {"type": "object", "additionalProperties": {"type": "string"}},
    },
}


class DecisionError(ValueError):
    """A close that does not satisfy `aos.decision.v1`."""


def validate_decision(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a decision record against the generic shape (04)."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        # Same constraints, enforced without the dependency (AA-10): 04's
        # nested shapes — dissent positions, follow-up fields, the embedded
        # resonance judgments — are constraints, not documentation.
        message = first_error(DECISION_SCHEMA, dict(record))
        if message is not None:
            raise DecisionError(f"{DECISION_SCHEMA_ID}: {message}") from None
        return dict(record)

    errors = sorted(
        Draft202012Validator(DECISION_SCHEMA).iter_errors(dict(record)),
        key=lambda error: list(error.path),
    )
    if errors:
        raise DecisionError(f"{DECISION_SCHEMA_ID}: {errors[0].message}")
    return dict(record)


@dataclass(frozen=True)
class ObligationBreach:
    """One chair obligation (04's table) the close does not satisfy."""

    obligation: str
    detail: str
    role: str | None = None

    def __str__(self) -> str:  # pragma: no cover - diagnostic convenience
        where = f" [{self.role}]" if self.role else ""
        return f"{self.obligation}{where}: {self.detail}"


def unmet_chair_obligations(
    record: Mapping[str, Any],
    *,
    judgments: Sequence[Mapping[str, Any]] | None = None,
    ledger: DeliberationLedger | None = None,
    open_follow_ups: Iterable[Mapping[str, Any]] = (),
    reviewed_follow_ups: Iterable[Mapping[str, Any]] = (),
    adversarial_round_held: bool = True,
) -> list[ObligationBreach]:
    """Check the close against 04's obligations table, exhaustively.

    Returns every breach rather than the first, because a close is reviewed
    as a whole. Obligations whose satisfaction is a judgment the chair
    states in prose (e.g. "say so, and record why" when deciding against the
    weight of resonance) are checked structurally — the presence of the
    record — never by second-guessing the reasoning.
    """
    breaches: list[ObligationBreach] = []
    judgments = list(judgments if judgments is not None else record.get("resonance") or [])
    dissent_roles = {entry.get("role") for entry in record.get("dissent") or []}
    overridden = {entry.get("role") for entry in record.get("overridden_vetoes") or []}

    for judgment in judgments:
        role = judgment.get("role")
        if is_domain_veto(judgment) and role not in overridden and role not in dissent_roles:
            breaches.append(
                ObligationBreach(
                    "domain veto neither resolved nor explicitly overridden",
                    "silent override is a defect; record the override and its rationale",
                    role,
                )
            )
        if is_recordable_dissent(judgment) and role not in dissent_roles:
            breaches.append(
                ObligationBreach(
                    "material low-resonance objection not recorded as dissent",
                    "record it whether or not the decision proceeds",
                    role,
                )
            )
        if needs_grounding(judgment) and not (record.get("rationale") or "").strip():
            breaches.append(
                ObligationBreach(
                    "low confidence on a high-relevance judgment closed without grounding",
                    "seek grounding before closing, or record why closing without it was acceptable",
                    role,
                )
            )

    if judgments and outside_roster_competence(judgments):
        if not (record.get("rationale") or "").strip():
            breaches.append(
                ObligationBreach(
                    "proposal outside the roster's competence",
                    "state that rather than manufacture a judgment",
                )
            )

    if ledger is not None:
        for role, position in ledger.unresolved_positions().items():
            if role not in dissent_roles:
                breaches.append(
                    ObligationBreach(
                        "unresolved position omitted from dissent",
                        f"position {position!r} was still held at close; unanimity "
                        "MUST NOT be manufactured by omission",
                        role,
                    )
                )
        if ledger.is_circling() and not (record.get("follow_ups") or record.get("decision")):
            breaches.append(
                ObligationBreach(
                    "room circling and neither decided nor deferred",
                    "force a decision on what is known, or defer with an explicit follow-up",
                )
            )

    reviewed = {(f.get("role"), f.get("action")) for f in reviewed_follow_ups}
    for follow_up in open_follow_ups:
        if (follow_up.get("role"), follow_up.get("action")) not in reviewed:
            breaches.append(
                ObligationBreach(
                    "prior open follow-up not reviewed at opening",
                    "name the owning participant and ask for status",
                    follow_up.get("role"),
                )
            )

    if not adversarial_round_held:
        breaches.append(
            ObligationBreach(
                "adversarial obligation unmet",
                "at least one round MUST invite explicit challenge rather than contribution",
            )
        )

    return breaches


def carry_forward_follow_ups(
    open_follow_ups: Iterable[Mapping[str, Any]], record: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Merge a close's new action items into standing open follow-ups (04).

    This is what gives follow-ups a lifecycle instead of write-only amnesia:
    the chair's next opening reviews what is here.
    """
    merged = [dict(entry) for entry in open_follow_ups]
    seen = {(entry.get("role"), entry.get("action")) for entry in merged}
    for follow_up in record.get("follow_ups") or []:
        key = (follow_up.get("role"), follow_up.get("action"))
        if key not in seen:
            merged.append(dict(follow_up))
            seen.add(key)
    return merged


__all__ = [
    "DECISION_SCHEMA",
    "DECISION_SCHEMA_ID",
    "POSITIONS",
    "RESONANCE_SCHEMA_ID",
    "DecisionError",
    "ObligationBreach",
    "carry_forward_follow_ups",
    "unmet_chair_obligations",
    "validate_decision",
]
