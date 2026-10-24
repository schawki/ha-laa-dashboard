// Loaded for every user. 1) the dashboard strategy `custom:laa-dashboard`; 2) the optional redirect of non-administrators.
import type { View } from "./types";
import { t } from "./i18n";

const tile = (entity: string) => ({ type: "tile", entity });

export function viewToConfig(v: View, lang?: string, title?: string) {
  const section = (name: string, entities: View["other"]) => {
    const cards: unknown[] = [{ type: "heading", heading: name }];
    for (const list of Object.values(entities)) for (const e of list) cards.push(tile(e.entity_id));
    return { type: "grid", cards };
  };
  const views = v.floors.map((f) => ({
    title: f.name || t(lang, "noFloor"), path: f.id.replace(/[^a-z0-9_]/gi, "") || "floor", type: "sections", max_columns: 4,
    sections: f.rooms.map((r) => section(r.name, r.entities)),
  }));
  if (Object.keys(v.other).length) views.push({ title: t(lang, "other"), path: "other", type: "sections", max_columns: 4, sections: [section(t(lang, "other"), v.other)] });
  if (!views.length) views.push({ title: title || "Maison", path: "empty", type: "sections", max_columns: 1, sections: [{ type: "grid", cards: [{ type: "markdown", content: t(lang, "previewEmpty") }] }] });
  return { title: title || "Maison", views };
}

class LaaStrategy extends HTMLElement {
  static async generate(config: { as_profile?: string; title?: string }, hass: any) {
    const v: View = await hass.callWS({ type: "laa_dashboard/view", ...(config.as_profile ? { as_profile: config.as_profile } : {}) });
    return viewToConfig(v, hass.language, config.title);
  }
}
if (!customElements.get("ll-strategy-dashboard-laa")) customElements.define("ll-strategy-dashboard-laa", LaaStrategy);
(window as any).customStrategies = (window as any).customStrategies || [];
(window as any).customStrategies.push({ type: "laa-dashboard", strategyType: "dashboard", name: "LAA Dashboard", description: "Rooms and entities filtered by user profile" });

// ---- redirect: once per browser session, only when Home Assistant is opened on its default page ----
const GUARD = "laa_dashboard_redirected";
export function shouldRedirect(path: string, done: boolean, me: { redirect: boolean }): boolean {
  return !done && me.redirect && (path === "/" || path === "/lovelace" || path.startsWith("/lovelace/"));
}
async function redirect() {
  try {
    if (sessionStorage.getItem(GUARD)) return;
  } catch { /* storage blocked: redirect at most once per page load below */ }
  const ha: any = document.querySelector("home-assistant");
  for (let i = 0; i < 50 && !(ha && ha.hass && ha.hass.connection); i++) await new Promise((r) => setTimeout(r, 200));
  if (!ha?.hass) return;
  try {
    const me = await ha.hass.callWS({ type: "laa_dashboard/me" });
    let done = false;
    try { done = !!sessionStorage.getItem(GUARD); sessionStorage.setItem(GUARD, "1"); } catch { /* ignore */ }
    if (shouldRedirect(location.pathname, done, me)) {
      history.pushState(null, "", `/${me.dashboard_path}`);
      window.dispatchEvent(new CustomEvent("location-changed"));
    }
  } catch { /* integration not ready: leave Home Assistant alone */ }
}
void redirect();
