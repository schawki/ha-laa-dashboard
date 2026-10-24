// Administrators' panel: profiles, "view as" preview, dashboard creation.
import { LitElement, html, css, nothing } from "lit";
import { property, state } from "lit/decorators.js";
import type { Catalog, Config, Profile, View } from "./types";
import { t, type Key } from "./i18n";

const uid = () => Math.random().toString(36).slice(2, 10);

class LaaPanel extends LitElement {
  @property({ attribute: false }) hass: any;
  @state() private cfg?: Config;
  @state() private cat?: Catalog;
  @state() private sel = "";
  @state() private previewAs = "";
  @state() private preview?: View;
  @state() private msg = "";
  private tr = (k: Key) => t(this.hass?.language, k);

  static styles = css`
    :host { display: block; padding: 16px; max-width: 1100px; margin: 0 auto; color: var(--primary-text-color); }
    h1 { font-weight: 400 } h2 { font-size: 1.1em; margin: 20px 0 8px } .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 6px 0 }
    .card { background: var(--card-background-color); border-radius: 12px; padding: 12px 16px; margin: 8px 0; box-shadow: var(--ha-card-box-shadow, none); border: 1px solid var(--divider-color) }
    .checks { display: flex; flex-wrap: wrap; gap: 4px 16px; max-height: 220px; overflow: auto } label { display: inline-flex; gap: 6px; align-items: center }
    button { padding: 8px 14px; border-radius: 8px; border: 1px solid var(--divider-color); background: var(--primary-color); color: var(--text-primary-color, #fff); cursor: pointer }
    button.plain { background: transparent; color: var(--primary-text-color) } .hint { color: var(--secondary-text-color); font-size: .9em }
    input[type=text], select, textarea { padding: 6px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: inherit }
    textarea { width: 100%; min-height: 56px; box-sizing: border-box } .tabs button { margin-right: 4px } .tabs button.on { outline: 2px solid var(--primary-color) }
    ul { margin: 4px 0 8px 18px; padding: 0 }
  `;

  async firstUpdated() {
    this.cat = await this.hass.callWS({ type: "laa_dashboard/catalog" });
    this.cfg = await this.hass.callWS({ type: "laa_dashboard/get_config" });
    this.sel = this.cfg!.profiles[0]?.id ?? "";
  }

  private get profile(): Profile | undefined { return this.cfg?.profiles.find((p) => p.id === this.sel); }
  private edit(patch: Partial<Profile>) {
    this.cfg = { ...this.cfg!, profiles: this.cfg!.profiles.map((p) => (p.id === this.sel ? { ...p, ...patch } : p)) };
  }
  private toggle(list: string[], v: string, on: boolean) { return on ? [...new Set([...list, v])] : list.filter((x) => x !== v); }
  private lines(s: string) { return s.split(/[\s,]+/).map((x) => x.trim()).filter(Boolean); }

  private addProfile() {
    const p: Profile = { id: uid(), name: this.tr("profiles") + " " + ((this.cfg!.profiles.length) + 1), user_ids: [], rooms_mode: "all", rooms: [], domains_mode: "all", domains: [],
      deny_domains: ["camera"], deny_entities: [], allow_entities: [] };
    this.cfg = { ...this.cfg!, profiles: [...this.cfg!.profiles, p] };
    this.sel = p.id;
  }
  private removeProfile() {
    const profiles = this.cfg!.profiles.filter((p) => p.id !== this.sel);
    this.cfg = { ...this.cfg!, profiles, default_profile_id: this.cfg!.default_profile_id === this.sel ? null : this.cfg!.default_profile_id };
    this.sel = profiles[0]?.id ?? "";
  }
  private async save() {
    this.cfg = await this.hass.callWS({ type: "laa_dashboard/save_config", ...this.cfg });
    this.msg = this.tr("saved");
    setTimeout(() => (this.msg = ""), 2500);
    if (this.previewAs) await this.loadPreview(this.previewAs);
  }
  private async loadPreview(as: string) {
    this.previewAs = as;
    this.preview = as ? await this.hass.callWS({ type: "laa_dashboard/view", ...(as === "__admin__" ? {} : { as_profile: as }) }) : undefined;
  }
  private async createDashboard() {
    const path = this.cfg!.dashboard_path;
    const existing: any[] = await this.hass.callWS({ type: "lovelace/dashboards/list" });
    if (existing.some((d) => d.url_path === path)) { this.msg = this.tr("dashboardExists"); return; }
    await this.hass.callWS({ type: "lovelace/dashboards/create", url_path: path, mode: "storage", title: this.tr("dashboardTitle"), icon: "mdi:home", show_in_sidebar: true, require_admin: false });
    await this.hass.callWS({ type: "lovelace/config/save", url_path: path, config: { strategy: { type: "custom:laa-dashboard" } } });
    this.msg = this.tr("dashboardCreated");
  }

  private checks(items: { id: string; name: string }[], chosen: string[], onChange: (id: string, on: boolean) => void) {
    return html`<div class="checks">${items.map((i) => html`<label><input type="checkbox" .checked=${chosen.includes(i.id)}
      @change=${(e: Event) => onChange(i.id, (e.target as HTMLInputElement).checked)} />${i.name}</label>`)}</div>`;
  }

  render() {
    if (!this.cfg || !this.cat) return nothing;
    const T = this.tr, p = this.profile, c = this.cat;
    const rooms = [{ id: "__none__", name: T("noRoom") }, ...c.areas.map((a) => ({ id: a.id, name: a.name }))];
    return html`
      <h1>${T("title")}</h1><p class="hint">${T("intro")}</p>
      <h2>${T("profiles")}</h2>
      <div class="tabs">${this.cfg.profiles.map((x) => html`<button class="plain ${x.id === this.sel ? "on" : ""}" @click=${() => (this.sel = x.id)}>${x.name}</button>`)}
        <button @click=${this.addProfile}>+ ${T("add")}</button></div>
      ${p ? html`<div class="card">
        <div class="row"><label>${T("name")} <input type="text" .value=${p.name} @input=${(e: Event) => this.edit({ name: (e.target as HTMLInputElement).value })} /></label>
          <button class="plain" @click=${this.removeProfile}>${T("remove")}</button></div>
        <h2>${T("users")}</h2>${this.checks(c.users.map((u) => ({ id: u.id, name: u.name + (u.is_admin ? ` (${T("administrator")})` : "") })), p.user_ids,
          (id, on) => this.edit({ user_ids: this.toggle(p.user_ids, id, on) }))}
        <h2>${T("rooms")}</h2>
        <select .value=${p.rooms_mode} @change=${(e: Event) => this.edit({ rooms_mode: (e.target as HTMLSelectElement).value as "all" | "selected" })}>
          <option value="all" ?selected=${p.rooms_mode === "all"}>${T("all")}</option><option value="selected" ?selected=${p.rooms_mode === "selected"}>${T("selected")}</option></select>
        ${p.rooms_mode === "selected" ? this.checks(rooms, p.rooms, (id, on) => this.edit({ rooms: this.toggle(p.rooms, id, on) })) : nothing}
        <h2>${T("domains")}</h2>
        <select .value=${p.domains_mode} @change=${(e: Event) => this.edit({ domains_mode: (e.target as HTMLSelectElement).value as "all" | "selected" })}>
          <option value="all" ?selected=${p.domains_mode === "all"}>${T("all")}</option><option value="selected" ?selected=${p.domains_mode === "selected"}>${T("selected")}</option></select>
        ${p.domains_mode === "selected" ? this.checks(c.domains.map((d) => ({ id: d, name: d })), p.domains, (id, on) => this.edit({ domains: this.toggle(p.domains, id, on) })) : nothing}
        <h2>${T("denyDomains")}</h2>${this.checks(c.domains.map((d) => ({ id: d, name: d })), p.deny_domains, (id, on) => this.edit({ deny_domains: this.toggle(p.deny_domains, id, on) }))}
        <p class="hint">${T("cameraNote")}</p>
        <h2>${T("denyEntities")}</h2><textarea .value=${p.deny_entities.join("\n")} @change=${(e: Event) => this.edit({ deny_entities: this.lines((e.target as HTMLTextAreaElement).value) })}></textarea>
        <h2>${T("allowEntities")}</h2><textarea .value=${p.allow_entities.join("\n")} @change=${(e: Event) => this.edit({ allow_entities: this.lines((e.target as HTMLTextAreaElement).value) })}></textarea>
      </div>` : nothing}
      <h2>${T("defaultProfile")}</h2>
      <select @change=${(e: Event) => (this.cfg = { ...this.cfg!, default_profile_id: (e.target as HTMLSelectElement).value || null })}>
        <option value="" ?selected=${!this.cfg.default_profile_id}>${T("noneDefault")}</option>
        ${this.cfg.profiles.map((x) => html`<option value=${x.id} ?selected=${x.id === this.cfg!.default_profile_id}>${x.name}</option>`)}</select>
      <h2>${T("dashboard")}</h2>
      <div class="row"><label>${T("dashboardPath")} <input type="text" .value=${this.cfg.dashboard_path} @input=${(e: Event) => (this.cfg = { ...this.cfg!, dashboard_path: (e.target as HTMLInputElement).value })} /></label>
        <button class="plain" @click=${this.createDashboard}>${T("createDashboard")}</button></div>
      <div class="row"><label><input type="checkbox" .checked=${this.cfg.redirect_non_admins} @change=${(e: Event) => (this.cfg = { ...this.cfg!, redirect_non_admins: (e.target as HTMLInputElement).checked })} /> ${T("redirect")}</label></div>
      <p class="hint">${T("redirectHint")}</p>
      <div class="row"><button @click=${this.save}>${T("save")}</button><span class="hint">${this.msg}</span></div>
      <h2>${T("preview")}</h2>
      <select @change=${(e: Event) => this.loadPreview((e.target as HTMLSelectElement).value)}>
        <option value="">${T("previewNone")}</option><option value="__admin__" ?selected=${this.previewAs === "__admin__"}>${T("previewAdmin")}</option>
        ${this.cfg.profiles.map((x) => html`<option value=${x.id} ?selected=${x.id === this.previewAs}>${x.name}</option>`)}</select>
      ${this.preview ? this.renderPreview(this.preview) : nothing}`;
  }

  private renderPreview(v: View) {
    const dom = (m: View["other"]) => Object.entries(m).map(([d, l]) => html`<li><b>${d}</b> (${l.length}): ${l.map((e) => e.name).join(", ")}</li>`);
    const empty = !v.floors.length && !Object.keys(v.other).length;
    return html`<div class="card">${empty ? html`<span class="hint">${this.tr("previewEmpty")}</span>` : nothing}
      ${v.floors.map((f) => html`<h3>${f.name ?? this.tr("noFloor")}</h3>${f.rooms.map((r) => html`<b>${r.name}</b><ul>${dom(r.entities)}</ul>`)}`)}
      ${Object.keys(v.other).length ? html`<h3>${this.tr("other")}</h3><ul>${dom(v.other)}</ul>` : nothing}</div>`;
  }
}
customElements.define("laa-dashboard-panel", LaaPanel);
