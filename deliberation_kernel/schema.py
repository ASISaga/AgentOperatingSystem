"""Fallback validation for the kernel's own schemas (`aos-spec` 03, 04).

``jsonschema`` is a declared dependency and stays the validator of record.
This module exists for the case where it is absent: the schemas in 03 and
04 state bounds, enums, types and closed objects, and a fallback that
checked only required-key presence let a judgment the spec forbids through
silently. Silent weakening is worse than a hard failure, so this enforces
the constraints those schemas actually declare.

It is deliberately not a general JSON Schema implementation. It covers the
keywords `aos.resonance.v1` and `aos.decision.v1` use — ``type``,
``required``, ``properties``, ``additionalProperties``, ``items``,
``enum``, ``minimum``, ``maximum`` — and raises rather than ignoring any
other constraint keyword, so that a schema growing a keyword this does not
understand cannot silently stop being enforced.
"""

from __future__ import annotations

from typing import Any, Iterator, Mapping, Sequence

#: Keywords that carry no constraint (identity/annotation only).
_ANNOTATION_KEYWORDS = frozenset({"$id", "$schema", "title", "description", "format"})

#: Keywords this validator enforces.
_SUPPORTED_KEYWORDS = frozenset(
    {
        "type",
        "required",
        "properties",
        "additionalProperties",
        "items",
        "enum",
        "minimum",
        "maximum",
    }
)


class UnsupportedSchema(NotImplementedError):
    """A schema keyword this fallback does not enforce.

    Raised rather than ignored: an unenforced constraint is exactly the
    defect this module was written to remove.
    """


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, Mapping)
    if expected == "array":
        return isinstance(instance, Sequence) and not isinstance(instance, (str, bytes))
    if expected == "string":
        return isinstance(instance, str)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "null":
        return instance is None
    raise UnsupportedSchema(f"unsupported type: {expected!r}")


def iter_errors(
    schema: Mapping[str, Any], instance: Any, path: tuple[Any, ...] = ()
) -> Iterator[tuple[tuple[Any, ...], str]]:
    """Yield ``(path, message)`` for every constraint the instance breaks."""
    unsupported = set(schema) - _SUPPORTED_KEYWORDS - _ANNOTATION_KEYWORDS
    if unsupported:
        raise UnsupportedSchema(
            f"schema keyword(s) not enforced by the fallback validator: {sorted(unsupported)}"
        )

    expected_type = schema.get("type")
    if expected_type is not None and not _type_matches(instance, expected_type):
        yield path, f"{instance!r} is not of type {expected_type!r}"
        return

    if "enum" in schema and instance not in schema["enum"]:
        yield path, f"{instance!r} is not one of {schema['enum']!r}"

    minimum = schema.get("minimum")
    maximum = schema.get("maximum")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if minimum is not None and instance < minimum:
            yield path, f"{instance!r} is less than the minimum of {minimum!r}"
        if maximum is not None and instance > maximum:
            yield path, f"{instance!r} is greater than the maximum of {maximum!r}"

    if isinstance(instance, Mapping):
        properties: Mapping[str, Any] = schema.get("properties") or {}
        for key in schema.get("required") or ():
            if key not in instance:
                yield path, f"{key!r} is a required property"
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in properties:
                yield from iter_errors(properties[key], value, path + (key,))
            elif additional is False:
                yield path, f"{key!r} was unexpected; additional properties are not allowed"
            elif isinstance(additional, Mapping):
                yield from iter_errors(additional, value, path + (key,))

    elif isinstance(instance, Sequence) and not isinstance(instance, (str, bytes)):
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, value in enumerate(instance):
                yield from iter_errors(items, value, path + (index,))


def first_error(schema: Mapping[str, Any], instance: Any) -> str | None:
    """The first error by path order, matching how the primary validator sorts."""
    errors = sorted(iter_errors(schema, instance), key=lambda error: [str(part) for part in error[0]])
    return errors[0][1] if errors else None


__all__ = ["UnsupportedSchema", "first_error", "iter_errors"]
