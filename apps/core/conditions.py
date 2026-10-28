"""Structured, validated conditions for dialogue, story branches, quests, lore and unlocks.

Administrators never write code. A condition is JSON built from these shapes:

    {}                                          always true (empty / null)
    {"all": [<cond>, ...]}                      every sub-condition holds
    {"any": [<cond>, ...]}                      at least one holds
    {"not": <cond>}                             negation
    {"quest": "<slug>", "state": "completed"}   state in: available, active, completed, failed
    {"lore": "<slug>"}                          lore entry discovered
    {"item": "<slug>"}                          artifact / item held
    {"world_visited": "<slug>"}                 world visited
    {"choice": "<key>", "equals": "<value>"}    a recorded player choice
    {"flag": "<name>", "equals": true}          arbitrary boolean/string/number flag
    {"page": "home"}                            website context (guide assistants)

The evaluator is a small interpreter over this grammar. There is no eval(), no attribute access,
and no expression language, so administrator input can never execute code.
"""
from dataclasses import dataclass, field

QUEST_STATES = {"available", "active", "completed", "failed"}
MAX_DEPTH = 8
MAX_NODES = 64
LEAF_KEYS = {"quest", "lore", "item", "world_visited", "choice", "flag", "page"}


class ConditionError(ValueError):
    pass


@dataclass
class ConditionContext:
    quest_states: dict = field(default_factory=dict)  # slug -> state
    discovered_lore: set = field(default_factory=set)
    items: set = field(default_factory=set)
    visited_worlds: set = field(default_factory=set)
    choices: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)
    page: str = ""

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        return cls(
            quest_states={str(k): str(v) for k, v in (data.get("quest_states") or {}).items()},
            discovered_lore=set(map(str, data.get("discovered_lore") or [])),
            items=set(map(str, data.get("items") or [])),
            visited_worlds=set(map(str, data.get("visited_worlds") or [])),
            choices={str(k): v for k, v in (data.get("choices") or {}).items()},
            flags={str(k): v for k, v in (data.get("flags") or {}).items()},
            page=str(data.get("page") or ""),
        )


def _is_scalar(value):
    return isinstance(value, (str, int, float, bool)) or value is None


def validate_condition(condition):
    """Return a list of human-readable problems (empty list = valid)."""
    errors = []
    counter = {"n": 0}

    def walk(node, path, depth):
        counter["n"] += 1
        if counter["n"] > MAX_NODES:
            errors.append("Condition is too large (more than 64 parts).")
            return
        if depth > MAX_DEPTH:
            errors.append(f"{path}: nested too deeply (max {MAX_DEPTH}).")
            return
        if not isinstance(node, dict):
            errors.append(f"{path}: each condition must be an object.")
            return
        if not node:
            return
        keys = set(node)
        if keys & {"all", "any"}:
            if len(keys) != 1:
                errors.append(f"{path}: 'all'/'any' must be the only key.")
                return
            key = next(iter(keys))
            items = node[key]
            if not isinstance(items, list) or not items:
                errors.append(f"{path}.{key}: must be a non-empty list.")
                return
            for i, item in enumerate(items):
                walk(item, f"{path}.{key}[{i}]", depth + 1)
            return
        if "not" in keys:
            if len(keys) != 1:
                errors.append(f"{path}: 'not' must be the only key.")
                return
            walk(node["not"], f"{path}.not", depth + 1)
            return
        leaf = keys & LEAF_KEYS
        if len(leaf) != 1:
            errors.append(f"{path}: unknown condition {sorted(keys)}. Use one of {sorted(LEAF_KEYS | {'all', 'any', 'not'})}.")
            return
        kind = next(iter(leaf))
        value = node[kind]
        if not isinstance(value, str) or not value.strip() or len(value) > 120:
            errors.append(f"{path}.{kind}: must be a non-empty text value (max 120 characters).")
        allowed = {kind}
        if kind == "quest":
            allowed.add("state")
            state = node.get("state", "completed")
            if state not in QUEST_STATES:
                errors.append(f"{path}.state: must be one of {sorted(QUEST_STATES)}.")
        if kind in {"flag", "choice"}:
            allowed.add("equals")
            if "equals" in node and not _is_scalar(node["equals"]):
                errors.append(f"{path}.equals: must be text, a number, true/false or null.")
        extra = keys - allowed
        if extra:
            errors.append(f"{path}: unexpected keys {sorted(extra)}.")

    if condition in (None, "", {}):
        return []
    walk(condition, "condition", 0)
    return errors


def evaluate(condition, ctx: ConditionContext) -> bool:
    """Evaluate a condition that has passed validate_condition(). Unknown shapes evaluate to False."""
    if condition in (None, "", {}):
        return True
    if not isinstance(condition, dict):
        return False
    if "all" in condition:
        return all(evaluate(c, ctx) for c in condition["all"])
    if "any" in condition:
        return any(evaluate(c, ctx) for c in condition["any"])
    if "not" in condition:
        return not evaluate(condition["not"], ctx)
    if "quest" in condition:
        return ctx.quest_states.get(condition["quest"]) == condition.get("state", "completed")
    if "lore" in condition:
        return condition["lore"] in ctx.discovered_lore
    if "item" in condition:
        return condition["item"] in ctx.items
    if "world_visited" in condition:
        return condition["world_visited"] in ctx.visited_worlds
    if "choice" in condition:
        return ctx.choices.get(condition["choice"]) == condition.get("equals", True)
    if "flag" in condition:
        return ctx.flags.get(condition["flag"]) == condition.get("equals", True)
    if "page" in condition:
        return ctx.page == condition["page"]
    return False


def referenced_slugs(condition):
    """Collect {"quest": {...}, "lore": {...}, "item": {...}, "world_visited": {...}} for reference checks."""
    found = {"quest": set(), "lore": set(), "item": set(), "world_visited": set()}

    def walk(node):
        if not isinstance(node, dict):
            return
        for key in ("all", "any"):
            if key in node and isinstance(node[key], list):
                for item in node[key]:
                    walk(item)
        if "not" in node:
            walk(node["not"])
        for key in found:
            if isinstance(node.get(key), str):
                found[key].add(node[key])

    walk(condition or {})
    return found


def check_references(condition):
    """Validate that referenced quests, lore, items and worlds exist. Returns a list of problems."""
    from apps.narrative.models import Artifact, LoreEntry
    from apps.quests.models import Quest
    from apps.worlds.models import World

    refs = referenced_slugs(condition)
    lookups = [("quest", Quest), ("lore", LoreEntry), ("item", Artifact), ("world_visited", World)]
    problems = []
    for key, model in lookups:
        if refs[key]:
            existing = set(model.objects.filter(slug__in=refs[key]).values_list("slug", flat=True))
            for slug in sorted(refs[key] - existing):
                problems.append(f"Unknown {key.replace('_visited', '')} '{slug}'.")
    return problems


def condition_validator(value):
    """Model-field validator: grammar + references."""
    from django.core.exceptions import ValidationError

    problems = validate_condition(value)
    if not problems:
        problems = check_references(value)
    if problems:
        raise ValidationError(problems)
