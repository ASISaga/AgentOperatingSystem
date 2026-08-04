"""M-4 — memory and domain-attributed tagging (`aos-spec/05-*`).

Every role in the domain application's catalog holds a memory slice from
the moment the catalog is defined — dormant slices are storage only, no
running agent and no purpose of their own. An active agent covering a
dormant role's domain tags its contributions explicitly, and those tagged
contributions are written into the dormant role's slice as well as its own.
The domain application supplies the catalog, the personas and the storage;
this module supplies the attribution and write-authority rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


class WriteAuthorityError(PermissionError):
    """A write outside the disjoint write-authority rule (05)."""


@dataclass(frozen=True)
class RoleCatalog:
    """Every eventual role, and which of them currently have live agents.

    ``chair`` is a member of ``active`` and additionally holds shared-state
    write authority (02).
    """

    roles: tuple[str, ...]
    active: tuple[str, ...]
    chair: str | None = None

    def __post_init__(self) -> None:
        unknown_active = [role for role in self.active if role not in self.roles]
        if unknown_active:
            raise ValueError(f"active roles absent from the catalog: {unknown_active}")
        if self.chair is not None and self.chair not in self.active:
            raise ValueError("the chair must be an active role")

    @property
    def dormant(self) -> tuple[str, ...]:
        return tuple(role for role in self.roles if role not in self.active)

    def is_dormant(self, role: str) -> bool:
        return role in self.dormant


def seed_slices(
    catalog: RoleCatalog, existing: Mapping[str, dict[str, Any]] | None = None
) -> dict[str, dict[str, Any]]:
    """Give every catalogued role a slice, active or not (05).

    Bounds the standing cost of a large role catalog to storage, not
    inference: a dormant slice has no agent, no deployment and no purpose.
    """
    slices = {role: dict((existing or {}).get(role) or {}) for role in catalog.roles}
    return slices


@dataclass(frozen=True)
class TaggedContribution:
    """One active agent's turn output, with the domains it materially touched.

    Tagging is EXPLICIT, not inferred (05): a missing or wrong tag is a
    visible prompt-quality defect, where inference would fail silently and
    unauditably.
    """

    role: str
    text: str
    domain_tags: tuple[str, ...] = ()

    def tags_for(self, catalog: RoleCatalog) -> tuple[str, ...]:
        """Tags that name a DORMANT role other than the acting agent's own.

        A tag naming an active role is dropped, not written: that role has
        its own agent, which writes its own slice. A tag naming an unknown
        role is a defect the caller sees as :class:`ValueError`.
        """
        unknown = [tag for tag in self.domain_tags if tag not in catalog.roles]
        if unknown:
            raise ValueError(f"{self.role} tagged roles absent from the catalog: {unknown}")
        return tuple(
            dict.fromkeys(
                tag for tag in self.domain_tags if tag != self.role and catalog.is_dormant(tag)
            )
        )


#: How a contribution becomes a slice entry. The domain application supplies
#: summarization; the mechanism supplies attribution.
Summarizer = Callable[[TaggedContribution, str], dict[str, Any]]


def _default_summary(contribution: TaggedContribution, target_role: str) -> dict[str, Any]:
    return {
        "attributed_to": contribution.role,
        "role": target_role,
        "text": contribution.text,
    }


def attributed_writes(
    contribution: TaggedContribution,
    catalog: RoleCatalog,
    *,
    summarize: Summarizer | None = None,
) -> dict[str, dict[str, Any]]:
    """Entries to write: the acting agent's own slice, plus tagged dormant ones.

    "IN ADDITION TO" is the whole point (05): content is never consolidated
    into the covering agent's slice alone, which is why a dormant role that
    later activates inherits a populated slice and needs no migration event.
    """
    summarize = summarize or _default_summary
    writes = {contribution.role: summarize(contribution, contribution.role)}
    for tag in contribution.tags_for(catalog):
        writes[tag] = summarize(contribution, tag)
    return writes


def check_write_authority(
    writer: str, target: str, catalog: RoleCatalog, *, shared_state: bool = False
) -> None:
    """Enforce disjoint write authority and its one exception (05).

    - each active participant writes only its own slice;
    - the chair additionally writes shared state;
    - ONE exception: an active agent MAY write a DORMANT role's slice via
      domain-attributed tagging — no active agent contends for it. The
      exception ends the moment that role activates.
    """
    if writer not in catalog.active:
        raise WriteAuthorityError(f"{writer} is not an active participant")
    if shared_state:
        if catalog.chair is None or writer != catalog.chair:
            raise WriteAuthorityError("only the chair writes shared state")
        return
    if target == writer:
        return
    if catalog.is_dormant(target):
        return
    raise WriteAuthorityError(
        f"{writer} may not write {target}'s slice: {target} is active and writes its own"
    )


def apply_writes(
    slices: dict[str, dict[str, Any]],
    writes: Mapping[str, dict[str, Any]],
    catalog: RoleCatalog,
    *,
    writer: str,
    key: str = "entries",
    limit: int = 20,
) -> dict[str, dict[str, Any]]:
    """Append attributed entries to their slices, checking authority first."""
    for target, entry in writes.items():
        check_write_authority(writer, target, catalog)
        slice_body = slices.setdefault(target, {})
        entries = list(slice_body.get(key) or [])[-(limit - 1) :]
        entries.append(entry)
        slice_body[key] = entries
    return slices


def missing_tag_candidates(
    contribution: TaggedContribution, catalog: RoleCatalog, mentions: Iterable[str]
) -> tuple[str, ...]:
    """Dormant roles the caller believes were touched but were not tagged.

    Checkability is the reason 05 chooses explicit tagging: this is what a
    prompt-quality test asserts against, and it never rewrites the tags.
    """
    tagged = set(contribution.domain_tags)
    return tuple(
        role for role in dict.fromkeys(mentions) if catalog.is_dormant(role) and role not in tagged
    )


__all__ = [
    "RoleCatalog",
    "Summarizer",
    "TaggedContribution",
    "WriteAuthorityError",
    "apply_writes",
    "attributed_writes",
    "check_write_authority",
    "missing_tag_candidates",
    "seed_slices",
]
