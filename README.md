# LAA Dashboard

*Location & Activity Aware Dashboard* for Home Assistant: a dashboard that adapts to who is looking at it. [Français](docs/README.fr.md)

> **Honest limits.** LAA Dashboard filters what the dashboard it builds *displays*. It is **not access control**: every logged-in Home Assistant user can still reach every entity through the API or by typing a page address. Do not rely on it to protect something sensitive.

## 0.1 — what it does

- **Profiles** (adult, child, guest…) attached to Home Assistant users. Each profile limits the rooms, the types of entities (domains) and the single entities shown.
- **Deny wins.** Order: hidden entity → shown entity → hidden type → rooms → types. **Cameras are hidden by default** for non-administrators; a profile can show them.
- **A dashboard strategy** (`custom:laa-dashboard`) that builds one view per floor with a section per room and native tile cards, from your areas and floors.
- **"View as"** preview in the administrators' panel.
- **Optional redirect** of non-administrators to the dashboard when they open Home Assistant (once per browser session).
- Users without a profile see the default profile, or nothing. Administrators see everything.

## Install

1. HACS → custom repository → this repository (category *Integration*), install, restart.
2. Settings → Devices & services → add **LAA Dashboard**.
3. Open **LAA Dashboard** in the sidebar (administrators): create profiles, assign users, then **Create the dashboard** (an ordinary storage dashboard using the strategy, visible to non-administrators) and save.

## Develop

`pip install pytest-homeassistant-custom-component && pytest`; `cd panel && npm ci && npm run build` (the bundles in `frontend/` are committed); `python panel/test/run.py` for the browser checks.

Roadmap: 0.2 user location (Bermuda, Frigate, voice satellites) and a live "Now" section · 0.3 situations and media in neighbouring rooms · 0.4 per-user blocks.
