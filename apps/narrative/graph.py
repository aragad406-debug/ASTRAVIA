"""Story-graph validation and layout for the Story Studio flow editor."""
from collections import defaultdict, deque

from apps.core.conditions import check_references, validate_condition

from .models import StoryBranch, StoryNode


def chapter_graph(chapter):
    nodes = list(chapter.nodes.select_related("speaker").order_by("order", "id"))
    node_ids = {n.id for n in nodes}
    branches = list(
        StoryBranch.objects.filter(from_node_id__in=node_ids).select_related("from_node", "to_node", "to_node__chapter")
    )
    return nodes, branches


def validate_chapter(chapter):
    """Return {"errors": [...], "warnings": [...]} describing structural problems."""
    errors, warnings = [], []
    nodes, branches = chapter_graph(chapter)
    if not nodes:
        warnings.append("This chapter has no story nodes yet (the chapter text is shown as linear prose).")
        return {"errors": errors, "warnings": warnings}

    by_id = {n.id: n for n in nodes}
    starts = [n for n in nodes if n.is_start]
    if not starts:
        errors.append("No start node. Mark exactly one node as the start.")
    elif len(starts) > 1:
        errors.append("More than one start node.")

    outgoing = defaultdict(list)
    for b in branches:
        outgoing[b.from_node_id].append(b)
        if b.to_node.chapter.arc_id != chapter.arc_id:
            errors.append(f"Branch {b.from_node.key} → {b.to_node.key} leaves the story arc.")
        problems = validate_condition(b.condition) or check_references(b.condition)
        for p in problems:
            errors.append(f"Branch {b.from_node.key} → {b.to_node.key}: {p}")

    for n in nodes:
        out = outgoing.get(n.id, [])
        if n.node_type == StoryNode.NodeType.ENDING:
            if out:
                errors.append(f"Ending node '{n.key}' must not have outgoing branches.")
            if not n.ending_type:
                errors.append(f"Ending node '{n.key}' has no ending type.")
        else:
            if not out:
                errors.append(f"Node '{n.key}' is a dead end. Add a branch or make it an ending.")
        if n.node_type == StoryNode.NodeType.CHOICE:
            if len(out) < 2:
                warnings.append(f"Choice node '{n.key}' offers fewer than two options.")
            for b in out:
                if not (b.label_en or b.label_ar):
                    errors.append(f"Choice '{n.key}' → '{b.to_node.key}' needs choice text.")
                elif not (b.label_en and b.label_ar):
                    warnings.append(f"Choice '{n.key}' → '{b.to_node.key}' is missing a translation.")
            unconditional = [b for b in out if not b.condition]
            if out and not unconditional:
                warnings.append(f"Every option at '{n.key}' is conditional; the player could be left with no choice.")

    if len(starts) == 1:
        seen, queue = {starts[0].id}, deque([starts[0].id])
        while queue:
            current = queue.popleft()
            for b in outgoing.get(current, []):
                if b.to_node_id in by_id and b.to_node_id not in seen:
                    seen.add(b.to_node_id)
                    queue.append(b.to_node_id)
        for n in nodes:
            if n.id not in seen:
                incoming_external = any(b.to_node_id == n.id for b in StoryBranch.objects.filter(to_node=n).exclude(from_node_id__in=by_id))
                if not incoming_external:
                    errors.append(f"Node '{n.key}' can never be reached from the start.")

    if not any(n.node_type == StoryNode.NodeType.ENDING for n in nodes) and not any(
        b.to_node.chapter_id != chapter.id for b in branches
    ):
        warnings.append("No ending node and no branch into another chapter: the chapter never concludes.")
    return {"errors": errors, "warnings": warnings}


def layout(chapter):
    """Layered layout (breadth-first depth from start) for the SVG flow view. Returns JSON-ready dict."""
    nodes, branches = chapter_graph(chapter)
    outgoing = defaultdict(list)
    for b in branches:
        outgoing[b.from_node_id].append(b.to_node_id)
    depth = {}
    start = next((n for n in nodes if n.is_start), nodes[0] if nodes else None)
    if start:
        depth[start.id] = 0
        queue = deque([start.id])
        while queue:
            cur = queue.popleft()
            for nxt in outgoing[cur]:
                if nxt not in depth:
                    depth[nxt] = depth[cur] + 1
                    queue.append(nxt)
    max_depth = max(depth.values(), default=0)
    for n in nodes:
        if n.id not in depth:
            max_depth += 1
            depth[n.id] = max_depth  # unreachable nodes are drawn on their own column
    columns = defaultdict(list)
    for n in nodes:
        columns[depth[n.id]].append(n)
    positioned = []
    for col, items in sorted(columns.items()):
        for row, n in enumerate(items):
            positioned.append({
                "id": n.id, "key": n.key, "type": n.node_type, "title": n.title_en or n.key,
                "start": n.is_start, "ending": n.ending_type, "x": col, "y": row,
            })
    edges = [
        {"from": b.from_node_id, "to": b.to_node_id, "label": b.label_en or b.label_ar or "",
         "conditional": bool(b.condition), "external": b.to_node.chapter_id != chapter.id}
        for b in branches
    ]
    return {"nodes": positioned, "edges": edges}
