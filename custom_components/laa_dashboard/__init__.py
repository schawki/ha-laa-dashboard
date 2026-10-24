"""LAA Dashboard (Location & Activity Aware Dashboard): a dashboard that adapts to who looks at it.

0.1: profiles that limit what each user sees (rooms, domains, entities; cameras hidden by default), a dashboard strategy, a preview
("view as") and an optional redirect of non-administrators to the dashboard. The filtering is cosmetic: Home Assistant's own API stays open
to every logged-in user, so this is not access control."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import websocket_api as ws
from .const import DOMAIN, GLOBAL_FILE, PANEL_FILE, PANEL_PATH, PANEL_URL

FRONTEND_DIR = Path(__file__).parent / "frontend"


def _version(name: str) -> int:
    p = FRONTEND_DIR / name
    return p.stat().st_mtime_ns if p.exists() else 0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not hass.data.get(f"{DOMAIN}_registered"):
        hass.data[f"{DOMAIN}_registered"] = True
        ws.async_register(hass)
        await hass.http.async_register_static_paths([StaticPathConfig(PANEL_URL, str(FRONTEND_DIR), cache_headers=False)])
        frontend.add_extra_js_url(hass, f"{PANEL_URL}/{GLOBAL_FILE}?v={_version(GLOBAL_FILE)}")      # strategy + redirect, for every user
        await panel_custom.async_register_panel(
            hass, webcomponent_name="laa-dashboard-panel", frontend_url_path=PANEL_PATH, module_url=f"{PANEL_URL}/{PANEL_FILE}?v={_version(PANEL_FILE)}",
            sidebar_title="LAA Dashboard", sidebar_icon="mdi:view-dashboard-variant", require_admin=True, config={}, embed_iframe=False)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    if hass.data.pop(f"{DOMAIN}_registered", None):
        frontend.async_remove_panel(hass, PANEL_PATH)
