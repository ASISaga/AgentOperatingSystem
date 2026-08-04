"""M-2 — resonance scoring (`aos-spec/03-resonance-scoring.md`).

A resonance judgment is produced by a participant's own reasoning, as a
judgment. Nothing in this module computes a score: it defines the shape a
judgment must have, the anchoring text that makes the scale mean the same
thing in every role prompt, the threshold predicates the chair's
obligations (04) are stated in terms of, and the structural refusal of any
cross-role arithmetic.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from deliberation_kernel.schema import first_error

RESONANCE_SCHEMA_ID = "aos.resonance.v1"

#: The generic judgment shape (03). A domain application MAY carry extra
#: fields on its own record; the judgment itself is closed, because an
#: unrecognised key here is a prompt defect, not an extension point.
RESONANCE_SCHEMA: dict[str, Any] = {
    "$id": RESONANCE_SCHEMA_ID,
    "type": "object",
    "additionalProperties": False,
    "required": ["role", "rationale", "score", "confidence", "domain_relevance"],
    "properties": {
        "role": {"type": "string"},
        "rationale": {
            "type": "string",
            "description": "MUST be produced BEFORE the score (anchoring rules)",
        },
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence": {"enum": ["low", "medium", "high"]},
        "domain_relevance": {"type": "number", "minimum": 0, "maximum": 1},
    },
}

#: Anchors (03). Concrete referents, required in EVERY role prompt — an
#: unanchored 0..1 scale is a number, not a judgment.
ANCHORS: tuple[tuple[float, float, str], ...] = (
    (0.9, 1.0, "directly advances the core commitment of this participant's purpose"),
    (0.6, 0.8, "advances it, with reservations stated in rationale"),
    (0.4, 0.6, "orthogonal; neither advances nor undermines"),
    (0.2, 0.4, "in tension with the purpose; proceeding has a real cost"),
    (0.0, 0.2, "actively undermines the purpose"),
)

#: Ready to interpolate into any role prompt. Domain applications MAY
#: substitute domain-specific wording (09, M-2 notes) but MUST keep the
#: bands and the rationale-before-score rule.
ANCHOR_PROMPT_BLOCK = "\n".join(
    ["Resonance scale (anchored; state rationale BEFORE the score):"]
    + [f"- {low:.1f}-{high:.1f} {text}" for low, high, text in ANCHORS]
)

#: Threshold constants the chair's obligations (04) are expressed against.
DOMAIN_VETO_SCORE = 0.2
DISSENT_SCORE = 0.4
DOMAIN_RELEVANCE_FLOOR = 0.6


class ResonanceError(ValueError):
    """A judgment that does not satisfy `aos.resonance.v1`."""


class CommensurabilityError(TypeError):
    """Raised on any attempt at cross-role arithmetic over resonance (03).

    Scores are valid ordinally within one role and as threshold signals
    across roles. Participants reason with different purposes, personas and
    (potentially) different models, so a mean or weighted average of their
    scores is a number with no referent. Aggregation is rule-based — see
    :mod:`deliberation_kernel.decision`.
    """


def validate_resonance(judgment: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one judgment, including the rationale-before-score rule.

    ``json.loads`` preserves key order, so "rationale MUST precede score"
    (03) is a checkable property of the emitted object rather than an
    exhortation in a prompt.
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        Draft202012Validator = None  # type: ignore[assignment]

    if Draft202012Validator is not None:
        errors = sorted(
            Draft202012Validator(RESONANCE_SCHEMA).iter_errors(dict(judgment)),
            key=lambda error: list(error.path),
        )
        if errors:
            raise ResonanceError(f"{RESONANCE_SCHEMA_ID}: {errors[0].message}")
    else:
        # Same constraints, enforced without the dependency: bounds and enums
        # are part of what 03 declares, so a fallback that checked only
        # required keys accepted judgments the spec forbids (AA-10).
        message = first_error(RESONANCE_SCHEMA, dict(judgment))
        if message is not None:
            raise ResonanceError(f"{RESONANCE_SCHEMA_ID}: {message}")

    keys = list(judgment)
    if keys.index("rationale") > keys.index("score"):
        raise ResonanceError(
            f"{RESONANCE_SCHEMA_ID}: rationale MUST precede score; a score "
            "without preceding reasoning is a defect (03)"
        )
    return dict(judgment)


def in_domain(judgment: Mapping[str, Any]) -> bool:
    """Whether the proposal falls within this participant's domain at all."""
    return float(judgment["domain_relevance"]) >= DOMAIN_RELEVANCE_FLOOR


def is_domain_veto(judgment: Mapping[str, Any]) -> bool:
    """Score below 0.2 from a participant whose domain this is (04)."""
    return in_domain(judgment) and float(judgment["score"]) < DOMAIN_VETO_SCORE


def is_recordable_dissent(judgment: Mapping[str, Any]) -> bool:
    """Score below 0.4 from a participant whose domain this is (04)."""
    return in_domain(judgment) and float(judgment["score"]) < DISSENT_SCORE


def needs_grounding(judgment: Mapping[str, Any]) -> bool:
    """High domain relevance held with low confidence (04)."""
    return in_domain(judgment) and judgment["confidence"] == "low"


def outside_roster_competence(judgments: Iterable[Mapping[str, Any]]) -> bool:
    """Every participant's domain relevance below the floor (04).

    An empty room is NOT outside competence — it is no room at all, and the
    caller has a different problem.
    """
    judgments = list(judgments)
    return bool(judgments) and not any(in_domain(j) for j in judgments)


def mean_resonance(judgments: Iterable[Mapping[str, Any]]) -> float:
    """Deliberately unimplemented: cross-role arithmetic is forbidden (03).

    This function exists so that the prohibition is discoverable at the one
    place someone would reach for it, and fails loudly rather than being a
    rule people are asked to remember.
    """
    raise CommensurabilityError(
        "resonance scores are not commensurable across roles; aggregate by "
        "the chair's rule-based obligations (04), never by arithmetic (03)"
    )


__all__ = [
    "ANCHORS",
    "ANCHOR_PROMPT_BLOCK",
    "CommensurabilityError",
    "DISSENT_SCORE",
    "DOMAIN_RELEVANCE_FLOOR",
    "DOMAIN_VETO_SCORE",
    "RESONANCE_SCHEMA",
    "RESONANCE_SCHEMA_ID",
    "ResonanceError",
    "in_domain",
    "is_domain_veto",
    "is_recordable_dissent",
    "mean_resonance",
    "needs_grounding",
    "outside_roster_competence",
    "validate_resonance",
]
