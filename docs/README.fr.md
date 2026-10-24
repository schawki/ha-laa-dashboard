# LAA Dashboard

*Location & Activity Aware Dashboard* pour Home Assistant : un tableau de bord qui s'adapte à la personne qui le regarde. [English](../README.md)

> **Limites.** LAA Dashboard filtre ce que le tableau de bord qu'il construit *affiche*. Ce n'est **pas un contrôle d'accès** : tout utilisateur connecté peut toujours atteindre toutes les entités via l'API ou en tapant l'adresse d'une page. Ne vous y fiez pas pour protéger quelque chose de sensible.

## 0.1 — ce que ça fait

- **Profils** (adulte, enfant, invité…) rattachés aux utilisateurs Home Assistant. Chaque profil limite les pièces, les types d'entités (domaines) et les entités affichées.
- **L'interdiction l'emporte.** Ordre : entité masquée → entité affichée → type masqué → pièces → types. **Les caméras sont masquées par défaut** pour les non-administrateurs ; un profil peut les afficher.
- **Une stratégie de tableau de bord** (`custom:laa-dashboard`) : une vue par étage, une section par pièce, des cartes tuiles natives, d'après vos zones et étages.
- **« Voir comme »** : aperçu dans le panneau des administrateurs.
- **Redirection facultative** des non-administrateurs vers le tableau de bord à l'ouverture de Home Assistant (une fois par session de navigateur).
- Un utilisateur sans profil reçoit le profil par défaut, ou rien. Les administrateurs voient tout.

## Installation

1. HACS → dépôt personnalisé → ce dépôt (catégorie *Intégration*), installer, redémarrer.
2. Paramètres → Appareils et services → ajouter **LAA Dashboard**.
3. Ouvrir **LAA Dashboard** dans le menu latéral (administrateurs) : créer les profils, affecter les utilisateurs, puis **Créer le tableau de bord** (un tableau de bord ordinaire utilisant la stratégie, visible des non-administrateurs) et enregistrer.

Feuille de route : 0.2 position de l'utilisateur (Bermuda, Frigate, satellites vocaux) et section « Maintenant » · 0.3 situations et médias des pièces voisines · 0.4 blocs par utilisateur.
