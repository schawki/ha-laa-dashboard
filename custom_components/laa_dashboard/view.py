"""Builds what the dashboard shows: floors -> rooms -> entities by domain, already filtered for a profile. Pure over plain data."""
from __future__ import annotations

from . import rules

NO_FLOOR = "__nofloor__"
SKIP_ENTITY_CATEGORY = True


def build(floors: list[dict], areas: list[dict], entities: list[dict], profile: dict | None) -> dict:
    """floors [{id,name,level}], areas [{id,name,floor_id}], entities [{entity_id,name,domain,area_id}].

    Returns {floors: [{id, name, rooms: [{id, name, entities: {domain: [{entity_id, name}]}}]}], other: {domain: [...]}}.
    profile None = no filtering (administrator). Empty rooms and floors are left out."""
    def visible(e):
        return profile is None or rules.entity_visible(profile, e["entity_id"], e["domain"], e["area_id"])

    by_area: dict[str | None, list[dict]] = {}
    for e in entities:
        if visible(e):
            by_area.setdefault(e["area_id"], []).append(e)

    def grouped(items):
        out: dict[str, list[dict]] = {}
        for e in sorted(items, key=lambda e: (e["domain"], e["name"].casefold(), e["entity_id"])):
            out.setdefault(e["domain"], []).append({"entity_id": e["entity_id"], "name": e["name"]})
        return out

    known = {a["id"] for a in areas}
    floor_ids = {f["id"] for f in floors}
    result = []
    order = sorted(floors, key=lambda f: (f.get("level") is None, f.get("level") or 0, f["name"].casefold()))
    groups = [(f["id"], f["name"]) for f in order] + [(NO_FLOOR, None)]
    for fid, fname in groups:
        rooms = []
        for a in sorted(areas, key=lambda a: a["name"].casefold()):
            if (a.get("floor_id") if a.get("floor_id") in floor_ids else NO_FLOOR) != fid:
                continue
            ents = by_area.get(a["id"], [])
            if ents:
                rooms.append({"id": a["id"], "name": a["name"], "entities": grouped(ents)})
        if rooms:
            result.append({"id": fid, "name": fname, "rooms": rooms})
    other = [e for aid, items in by_area.items() if aid is None or aid not in known for e in items]
    return {"floors": result, "other": grouped(other)}
