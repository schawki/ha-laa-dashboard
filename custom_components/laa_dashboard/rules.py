"""What a profile may see. Pure functions, no Home Assistant objects: easy to test.

A profile is {id, name, user_ids, rooms_mode, rooms, domains_mode, domains, deny_domains, deny_entities, allow_entities}.
Order of the rules (the first that applies wins):
  1. entity in deny_entities            -> hidden (deny always wins)
  2. entity in allow_entities           -> shown, whatever its room or domain
  3. domain in deny_domains             -> hidden
  4. rooms_mode == "selected" and the room is not in rooms (an entity without a room counts as "no room") -> hidden
  5. domains_mode == "selected" and the domain is not in domains -> hidden
  6. otherwise shown
Administrators are never filtered, unless an administrator previews a profile ("view as")."""
from __future__ import annotations

from .const import DEFAULT_DENY_DOMAINS

NO_ROOM = "__none__"


def new_profile(pid: str, name: str, **kw) -> dict:
    p = {"id": pid, "name": name, "user_ids": [], "rooms_mode": "all", "rooms": [], "domains_mode": "all", "domains": [],
         "deny_domains": list(DEFAULT_DENY_DOMAINS), "deny_entities": [], "allow_entities": []}
    p.update(kw)
    return normalize(p)


def normalize(p: dict) -> dict:
    """A clean copy: unknown keys dropped, lists de-duplicated, modes checked."""
    def lst(k):
        return sorted({str(x) for x in (p.get(k) or []) if x})
    return {"id": str(p["id"]), "name": str(p.get("name") or p["id"]).strip() or str(p["id"]),
            "user_ids": lst("user_ids"),
            "rooms_mode": "selected" if p.get("rooms_mode") == "selected" else "all", "rooms": lst("rooms"),
            "domains_mode": "selected" if p.get("domains_mode") == "selected" else "all", "domains": lst("domains"),
            "deny_domains": lst("deny_domains"), "deny_entities": lst("deny_entities"), "allow_entities": lst("allow_entities")}


def entity_visible(profile: dict, entity_id: str, domain: str, area_id: str | None) -> bool:
    if entity_id in profile["deny_entities"]:
        return False
    if entity_id in profile["allow_entities"]:
        return True
    if domain in profile["deny_domains"]:
        return False
    if profile["rooms_mode"] == "selected" and (area_id or NO_ROOM) not in profile["rooms"]:
        return False
    if profile["domains_mode"] == "selected" and domain not in profile["domains"]:
        return False
    return True


def profile_for_user(profiles: list[dict], default_id: str | None, user_id: str) -> dict | None:
    """The first profile that lists the user, else the default profile, else None (None = nothing shown but a notice)."""
    for p in profiles:
        if user_id in p["user_ids"]:
            return p
    return next((p for p in profiles if p["id"] == default_id), None)
