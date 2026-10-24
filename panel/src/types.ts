export interface Profile {
  id: string; name: string; user_ids: string[]; rooms_mode: "all" | "selected"; rooms: string[]; domains_mode: "all" | "selected"; domains: string[];
  deny_domains: string[]; deny_entities: string[]; allow_entities: string[];
}
export interface Config { profiles: Profile[]; default_profile_id: string | null; redirect_non_admins: boolean; dashboard_path: string }
export interface Catalog {
  users: { id: string; name: string; is_admin: boolean }[]; floors: { id: string; name: string; level: number | null }[];
  areas: { id: string; name: string; floor_id: string | null }[]; domains: string[]; entities: { entity_id: string; name: string; domain: string }[];
}
export interface View {
  profile: { id: string; name: string } | null;
  floors: { id: string; name: string | null; rooms: { id: string; name: string; entities: Record<string, { entity_id: string; name: string }[]> }[] }[];
  other: Record<string, { entity_id: string; name: string }[]>;
}
