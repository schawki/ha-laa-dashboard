"""WebSocket commands. `view` and `me` are open to every logged-in user (they only return what the user's profile allows);
everything else is for administrators."""
from __future__ import annotations

import uuid

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er, floor_registry as fr

from . import rules, view
from .const import (DEFAULT_DASHBOARD_PATH, DOMAIN, OPT_DASHBOARD_PATH, OPT_DEFAULT_PROFILE, OPT_PROFILES, OPT_REDIRECT)


def _entry(hass: HomeAssistant):
    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if entries else None


def get_config(hass: HomeAssistant) -> dict:
    e = _entry(hass)
    o = e.options if e else {}
    profiles = [rules.normalize(p) for p in o.get(OPT_PROFILES, [])]
    default = o.get(OPT_DEFAULT_PROFILE)
    return {"profiles": profiles, "default_profile_id": default if any(p["id"] == default for p in profiles) else None,
            "redirect_non_admins": bool(o.get(OPT_REDIRECT, False)), "dashboard_path": o.get(OPT_DASHBOARD_PATH) or DEFAULT_DASHBOARD_PATH}


def collect(hass: HomeAssistant) -> tuple[list[dict], list[dict], list[dict]]:
    """Floors, areas and entities worth showing (no disabled, hidden or diagnostic/config entities, none of this integration's own)."""
    floors = [{"id": f.floor_id, "name": f.name, "level": f.level} for f in fr.async_get(hass).floors.values()]
    areas = [{"id": a.id, "name": a.name, "floor_id": a.floor_id} for a in ar.async_get(hass).areas.values()]
    devices = dr.async_get(hass)
    entities = []
    for e in er.async_get(hass).entities.values():
        if e.platform == DOMAIN or e.disabled or e.hidden_by or e.entity_category is not None:
            continue
        device = devices.async_get(e.device_id) if e.device_id else None
        state = hass.states.get(e.entity_id)
        entities.append({"entity_id": e.entity_id, "domain": e.domain, "area_id": e.area_id or (device.area_id if device else None),
                         "name": (state.name if state else None) or e.name or e.original_name or e.entity_id})
    return floors, areas, entities


def build_view(hass: HomeAssistant, user, as_profile: str | None = None) -> dict:
    cfg = get_config(hass)
    floors, areas, entities = collect(hass)
    profile = None
    if as_profile is not None and user.is_admin:
        profile = next((p for p in cfg["profiles"] if p["id"] == as_profile), None)
    elif not user.is_admin:
        profile = rules.profile_for_user(cfg["profiles"], cfg["default_profile_id"], user.id)
        if profile is None:        # a non-administrator with no profile and no default one sees nothing
            return {"profile": None, "floors": [], "other": {}}
    out = view.build(floors, areas, entities, profile)
    out["profile"] = {"id": profile["id"], "name": profile["name"]} if profile else None
    return out


def _admin(func):
    return websocket_api.require_admin(websocket_api.async_response(func))


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_view)
    websocket_api.async_register_command(hass, ws_me)
    websocket_api.async_register_command(hass, ws_get_config)
    websocket_api.async_register_command(hass, ws_save_config)
    websocket_api.async_register_command(hass, ws_catalog)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/view", vol.Optional("as_profile"): str})
@websocket_api.async_response
async def ws_view(hass, connection, msg):
    if msg.get("as_profile") is not None and not connection.user.is_admin:
        connection.send_error(msg["id"], "unauthorized", "Only administrators can preview a profile")
        return
    connection.send_result(msg["id"], build_view(hass, connection.user, msg.get("as_profile")))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/me"})
@websocket_api.async_response
async def ws_me(hass, connection, msg):
    cfg = get_config(hass)
    u = connection.user
    connection.send_result(msg["id"], {"is_admin": u.is_admin, "redirect": cfg["redirect_non_admins"] and not u.is_admin,
                                       "dashboard_path": cfg["dashboard_path"]})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_config"})
@_admin
async def ws_get_config(hass, connection, msg):
    connection.send_result(msg["id"], get_config(hass))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/save_config", vol.Required("profiles"): [dict],
                                  vol.Optional("default_profile_id"): vol.Any(str, None), vol.Optional("redirect_non_admins"): bool,
                                  vol.Optional("dashboard_path"): str})
@_admin
async def ws_save_config(hass, connection, msg):
    entry = _entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_loaded", "LAA Dashboard is not set up")
        return
    profiles, seen = [], set()
    for raw in msg["profiles"]:
        raw = dict(raw)
        raw["id"] = str(raw.get("id") or uuid.uuid4().hex[:8])
        if raw["id"] in seen:
            connection.send_error(msg["id"], "invalid_format", "Duplicate profile id")
            return
        seen.add(raw["id"])
        profiles.append(rules.normalize(raw))
    default = msg.get("default_profile_id")
    options = {**entry.options, OPT_PROFILES: profiles, OPT_DEFAULT_PROFILE: default if default in seen else None}
    if "redirect_non_admins" in msg:
        options[OPT_REDIRECT] = msg["redirect_non_admins"]
    if msg.get("dashboard_path"):
        options[OPT_DASHBOARD_PATH] = msg["dashboard_path"].strip("/ ")
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], get_config(hass))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/catalog"})
@_admin
async def ws_catalog(hass, connection, msg):
    """What the panel offers to pick from: users, rooms (with their floor), domains in use, entities."""
    floors, areas, entities = collect(hass)
    users = [{"id": u.id, "name": u.name, "is_admin": u.is_admin} for u in await hass.auth.async_get_users() if u.is_active and not u.system_generated]
    domains = sorted({e["domain"] for e in entities})
    connection.send_result(msg["id"], {"users": users, "floors": floors, "areas": areas, "domains": domains,
                                       "entities": [{"entity_id": e["entity_id"], "name": e["name"], "domain": e["domain"]} for e in entities]})
