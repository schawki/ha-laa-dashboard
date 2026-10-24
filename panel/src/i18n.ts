// English is the reference; French follows the Home Assistant language.
const en = {
  title: "LAA Dashboard", intro: "Profiles decide what each person sees on the dashboard. This is a display filter, not access control: the Home Assistant API stays open to every logged-in user.",
  profiles: "Profiles", add: "Add a profile", remove: "Delete", name: "Name", users: "Users", rooms: "Rooms", domains: "Types of entities",
  all: "All", selected: "Only the selected ones", noRoom: "Entities without a room", denyDomains: "Always hidden types", denyEntities: "Always hidden entities",
  allowEntities: "Always shown entities", defaultProfile: "Profile for users without a profile", noneDefault: "None (they see nothing)",
  save: "Save", saved: "Saved", cameraNote: "Cameras are hidden by default. Remove \"camera\" from the hidden types to show them.",
  preview: "View as", previewNone: "Choose a profile", previewAdmin: "Administrator (everything)", previewEmpty: "Nothing to show for this profile.",
  other: "Other", noFloor: "No floor", redirect: "Send non-administrators to the dashboard when they open Home Assistant",
  redirectHint: "Cosmetic: they can still open any page by typing its address.", dashboard: "Dashboard", dashboardPath: "Address of the dashboard",
  createDashboard: "Create the dashboard", dashboardExists: "The dashboard exists", dashboardCreated: "Dashboard created", dashboardTitle: "Maison",
  administrator: "administrator", none: "none", entitiesCount: "entities",
};
const fr: typeof en = {
  title: "LAA Dashboard", intro: "Les profils décident de ce que chacun voit sur le tableau de bord. C'est un filtre d'affichage, pas un contrôle d'accès : l'API de Home Assistant reste ouverte à tout utilisateur connecté.",
  profiles: "Profils", add: "Ajouter un profil", remove: "Supprimer", name: "Nom", users: "Utilisateurs", rooms: "Pièces", domains: "Types d'entités",
  all: "Toutes", selected: "Seulement celles cochées", noRoom: "Entités sans pièce", denyDomains: "Types toujours masqués", denyEntities: "Entités toujours masquées",
  allowEntities: "Entités toujours affichées", defaultProfile: "Profil des utilisateurs sans profil", noneDefault: "Aucun (ils ne voient rien)",
  save: "Enregistrer", saved: "Enregistré", cameraNote: "Les caméras sont masquées par défaut. Retirez « camera » des types masqués pour les afficher.",
  preview: "Voir comme", previewNone: "Choisir un profil", previewAdmin: "Administrateur (tout)", previewEmpty: "Rien à afficher pour ce profil.",
  other: "Autres", noFloor: "Sans étage", redirect: "Envoyer les non-administrateurs vers le tableau de bord à l'ouverture de Home Assistant",
  redirectHint: "Cosmétique : ils peuvent toujours ouvrir une page en tapant son adresse.", dashboard: "Tableau de bord", dashboardPath: "Adresse du tableau de bord",
  createDashboard: "Créer le tableau de bord", dashboardExists: "Le tableau de bord existe", dashboardCreated: "Tableau de bord créé", dashboardTitle: "Maison",
  administrator: "administrateur", none: "aucun", entitiesCount: "entités",
};
export type Key = keyof typeof en;
export const t = (lang: string | undefined, k: Key): string => ((lang || "en").startsWith("fr") ? fr : en)[k];
