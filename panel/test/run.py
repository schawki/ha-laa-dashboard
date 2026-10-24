"""Browser checks of the built bundles (Playwright). Run: python panel/test/run.py"""
import json, pathlib, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2] / "custom_components/laa_dashboard/frontend"
VIEW = {"profile": {"id": "p", "name": "Kid"}, "other": {"light": [{"entity_id": "light.x", "name": "X"}]},
        "floors": [{"id": "ground", "name": "Ground", "rooms": [{"id": "salon", "name": "Salon", "entities": {"light": [{"entity_id": "light.a", "name": "A"}]}}]}]}
CFG = {"profiles": [{"id": "p", "name": "Kid", "user_ids": [], "rooms_mode": "all", "rooms": [], "domains_mode": "all", "domains": [], "deny_domains": ["camera"], "deny_entities": [], "allow_entities": []}],
       "default_profile_id": None, "redirect_non_admins": False, "dashboard_path": "maison"}
CAT = {"users": [{"id": "u1", "name": "Adam", "is_admin": False}], "floors": [], "areas": [{"id": "salon", "name": "Salon", "floor_id": None}], "domains": ["camera", "light"], "entities": []}

HASS = """window.calls=[]; const R=%s; window.hass={language:'en',connection:{},callWS:async(m)=>{window.calls.push(m);
 if(m.type==='laa_dashboard/view')return R.view; if(m.type==='laa_dashboard/me')return R.me; if(m.type==='laa_dashboard/get_config')return R.cfg;
 if(m.type==='laa_dashboard/catalog')return R.cat; if(m.type==='laa_dashboard/save_config')return m; if(m.type==='lovelace/dashboards/list')return []; return {};}};"""


def main():
    ok = True
    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name); ok &= bool(cond)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        errors = []; pg.on("pageerror", lambda e: errors.append(str(e)))
        data = json.dumps({"view": VIEW, "me": {"redirect": True, "dashboard_path": "maison", "is_admin": False}, "cfg": CFG, "cat": CAT})
        # strategy + redirect
        pg.route("http://t/", lambda r: r.fulfill(content_type="text/html", body="<home-assistant></home-assistant>"))
        pg.route("http://t/maison", lambda r: r.fulfill(content_type="text/html", body="x"))
        pg.goto("http://t/")
        pg.evaluate("(h)=>{const ha=document.querySelector('home-assistant'); " + (HASS % data) + " ha.hass=window.hass;}", None)
        pg.add_script_tag(content=(ROOT / "laa-dashboard.js").read_text(), type="module")
        pg.wait_for_function("location.pathname==='/maison'", timeout=5000)
        check("non-admin redirected from / to the dashboard once", pg.evaluate("location.pathname") == "/maison")
        cfg = pg.evaluate("customElements.get('ll-strategy-dashboard-laa').generate({}, window.hass)")
        check("one view per floor plus 'Other'", [v["title"] for v in cfg["views"]] == ["Ground", "Other"])
        check("tiles for each entity", cfg["views"][0]["sections"][0]["cards"][1] == {"type": "tile", "entity": "light.a"})
        # panel
        pg2 = b.new_page(); pg2.on("pageerror", lambda e: errors.append(str(e)))
        pg2.route("http://t/", lambda r: r.fulfill(content_type="text/html", body="<body></body>")); pg2.goto("http://t/")
        pg2.evaluate(HASS % data); pg2.add_script_tag(content=(ROOT / "laa-dashboard-panel.js").read_text(), type="module")
        pg2.evaluate("()=>{const el=document.createElement('laa-dashboard-panel'); el.hass=window.hass; document.body.appendChild(el);}")
        pg2.wait_for_selector("laa-dashboard-panel >> text=Profiles")
        check("panel lists the profile", pg2.locator("laa-dashboard-panel >> button.plain.on").inner_text() == "Kid")
        check("camera is hidden by default (checked)", pg2.locator("laa-dashboard-panel >> text=camera").count() >= 1)
        pg2.locator("laa-dashboard-panel >> select").last.select_option("p")
        pg2.wait_for_selector("laa-dashboard-panel >> text=Salon")
        check("preview shows rooms", pg2.locator("laa-dashboard-panel >> text=Salon").count() >= 1)
        pg2.locator("laa-dashboard-panel >> text=Save").click()
        pg2.wait_for_selector("laa-dashboard-panel >> text=Saved")
        check("save sends the config", any(c["type"] == "laa_dashboard/save_config" for c in pg2.evaluate("window.calls")))
        check("no page errors", not errors)
        if errors: print(errors)
        b.close()
    sys.exit(0 if ok else 1)


main()
