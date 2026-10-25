# Release_manager

## 1. Ce que tu construis

Une application web interne où des utilisateurs avec des **rôles différents** préparent des **releases** (des paquets de scripts SQL ordonnés) destinées à une **base cible**, et les font passer par un **workflow d'approbation**.

À la fin de la phase 1, l'application ne sait **pas encore exécuter** les scripts (c'est la phase 3). Elle sait en revanche :

- stocker des environnements, des bases cibles, des releases et leurs scripts ;
- faire respecter un workflow (brouillon → soumise → approuvée) ;
- restreindre chaque action selon le rôle ;
- exposer les releases par une API REST.

C'est le squelette sur lequel tout le reste se branchera.

## 2. Choix techniques de départ

| Élément | Choix | Pourquoi |
|---|---|---|
| Python | 3.12 ou plus récent, en environnement virtuel (`venv`) | Standard |
| Django | Version LTS la plus récente (5.2) | Stabilité, c'est ce qu'une entreprise choisit |
| API | Django REST Framework | Cité dans l'annonce (REST API) |
| Base pour l'instant | SQLite | Zéro installation. Oracle arrive en phase 2 |
| Configuration | Variables d'environnement (`django-environ`) | Habitude à prendre dès maintenant : aucun secret dans le code |
| Tests | `pytest-django` ou `TestCase` de Django | Un outil qui déploie des scripts SQL doit être testé |
| Git | Dépôt dès le premier jour, `.gitignore`, commits clairs | Git figure dans la liste de l'annonce |

**Attention :** SQLite sert seulement de support à *ton application*. La base Oracle sera la **cible** des scripts, un rôle très différent. Cette distinction est importante à comprendre.

## 3. Structure du projet

```
release_manager/
├── manage.py
├── config/                  # settings, urls, wsgi
├── releases/                # le cœur métier
│   ├── models.py
│   ├── services.py          # logique de workflow (transitions)
│   ├── permissions.py       # noms des permissions et des groupes
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── api/
│   │   ├── serializers.py
│   │   └── views.py
│   ├── templates/releases/
│   └── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Une seule application métier suffit pour l'instant. Tu en ajouteras une pour l'audit en phase 6.

## 4. Les modèles de données

### `Environnement`
| Champ | Type | Remarque |
|---|---|---|
| `code` | CharField, unique | `TEST`, `ACC`, `PROD` |
| `nom` | CharField | |
| `approbation_requise` | BooleanField | Vrai pour la production |
| `ordre` | PositiveInteger | Pour trier : test, puis acceptation, puis production |

### `BaseCible`
| Champ | Type | Remarque |
|---|---|---|
| `nom` | CharField | Nom lisible |
| `environnement` | ForeignKey | |
| `type_sgbd` | CharField avec choix | Pour l'instant une seule valeur : `ORACLE`. Ce champ prépare l'ouverture à d'autres SGBD |
| `dsn` | CharField | Adresse / nom de service |
| `chemin_secret` | CharField | **Le chemin du secret dans Vault, jamais le mot de passe.** Prépare la phase 5 |
| `active` | BooleanField | |

### `Release`
| Champ | Type | Remarque |
|---|---|---|
| `titre` | CharField | |
| `description` | TextField | |
| `base_cible` | ForeignKey | |
| `auteur` | ForeignKey vers `User` | |
| `statut` | CharField avec choix | Voir workflow ci-dessous |
| `approuvee_par` | ForeignKey vers `User`, nullable | |
| `approuvee_le` | DateTimeField, nullable | |
| `planifiee_le` | DateTimeField, nullable | Servira en phase 4 |
| `cree_le` / `modifie_le` | DateTimeField automatiques | |

### `Script`
| Champ | Type | Remarque |
|---|---|---|
| `release` | ForeignKey | |
| `ordre` | PositiveInteger | Unique par release (contrainte `unique_together` ou `UniqueConstraint`) |
| `nom` | CharField | Ex. `001_create_table_facture.sql` |
| `contenu` | TextField | Le SQL |
| `contenu_retour_arriere` | TextField, vide autorisé | Le script d'annulation, écrit à l'avance |
| `hash_contenu` | CharField | SHA-256 du contenu, calculé à l'enregistrement. Sert à prouver plus tard ce qui a été exécuté |

Le modèle `Execution` (statut, début, fin, sortie, erreur par script) viendra en phase 3. Ne le crée pas maintenant.

## 5. Le workflow à implémenter

**Statuts :** `BROUILLON` → `SOUMISE` → `APPROUVEE`, avec deux sorties possibles : `REFUSEE` et `ANNULEE`. Les statuts suivants (`PLANIFIEE`, `EN_COURS`, `TERMINEE`, `ECHEC`) seront ajoutés dans les phases 3 et 4. Déclare-les dès maintenant dans les choix si tu veux, mais n'implémente pas leurs transitions.

| Action | Depuis | Vers | Qui peut le faire |
|---|---|---|---|
| Soumettre | Brouillon | Soumise | L'auteur de la release |
| Approuver | Soumise | Approuvée | Un approbateur, **différent de l'auteur** |
| Refuser | Soumise | Refusée | Un approbateur |
| Annuler | Brouillon, Soumise | Annulée | L'auteur |
| Modifier les scripts | Brouillon uniquement | , | L'auteur |

**Règles métier à coder et à tester :**

1. **Séparation des tâches** : personne n'approuve sa propre release. C'est une règle d'audit classique, et elle fera très bien en entretien.
2. **Une release soumise ou approuvée n'est plus modifiable.** Sinon on pourrait faire approuver un script puis en changer le contenu.
3. **Une release sans script ne peut pas être soumise.**
4. **Les transitions invalides lèvent une erreur claire** (par exemple approuver un brouillon).
5. Les environnements avec `approbation_requise = False` pourraient permettre un raccourci : décide-le et documente-le.

**Bonne pratique à adopter :** mets la logique dans des fonctions de `services.py` (par exemple `soumettre(release, utilisateur)`), pas dans les vues. Les vues, l'admin et l'API appelleront les mêmes fonctions. C'est du *Single Responsibility* concret, et c'est facile à tester.

## 6. Rôles et permissions

Quatre groupes Django, créés par une migration de données ou une commande de gestion :

| Groupe | Peut |
|---|---|
| **Lecteur** | Voir les releases |
| **Auteur** | Lecteur + créer et modifier ses brouillons, soumettre |
| **Approbateur** | Lecteur + approuver ou refuser |
| **Exécutant** | Lecteur + (plus tard) planifier et lancer |

Utilise le mécanisme de **permissions personnalisées** de Django (`Meta.permissions`, par exemple `approuver_release`) plutôt que de tester des noms de groupes dans le code. On teste « a-t-il la permission ? », pas « est-il dans le groupe ? ». C'est plus propre et plus flexible.

## 7. Les écrans et l'API

**Admin Django** (rapide, sert de back-office) :
- Environnements et bases cibles gérés ici.
- Releases avec leurs scripts en *inline*.
- Filtres par statut et par environnement.

**Pages personnalisées** (minimum) :
- Liste des releases avec filtres (statut, environnement).
- Détail d'une release : informations, scripts dans l'ordre, boutons d'action visibles seulement si l'utilisateur y a droit.
- Création et édition d'un brouillon.
- Connexion et déconnexion.

**API REST (DRF)**, volontairement réduite :
- `GET /api/releases/` et `GET /api/releases/{id}/`
- `POST /api/releases/{id}/soumettre/`, `/approuver/`, `/refuser/`
- Authentification par session au départ, avec les mêmes permissions que l'interface.

## 8. Tests à écrire

Pas besoin de couverture totale, mais ces cas-là doivent exister :

- Un auteur ne peut pas approuver sa propre release.
- Impossible de soumettre une release sans script.
- Impossible de modifier un script après soumission.
- Un lecteur ne peut pas soumettre ni approuver.
- Une transition invalide est refusée.
- Le hash d'un script change quand son contenu change.

## 9. Déroulé sur 2 jours

**Jour 1 : fondations**
1. Dépôt Git, environnement virtuel, projet Django, `requirements.txt`, `.gitignore`, `.env.example`.
2. Modèles + migrations.
3. Admin configuré (inlines, filtres).
4. Groupes et permissions créés automatiquement.
5. Jeu de données d'exemple (une commande qui crée environnements, une base cible et une release).

**Jour 2 : logique et accès**
1. `services.py` avec les transitions et leurs règles.
2. Tests de ces règles.
3. Vues liste, détail, création, avec contrôle des permissions.
4. API DRF réduite.
5. README (comment lancer, schéma des modèles, workflow) et commit propre.

## 10. Critères de réussite

Tu as terminé la phase 1 quand :

- [ ] Je peux lancer le projet en suivant ton README seul.
- [ ] Je peux me connecter avec trois comptes (auteur, approbateur, lecteur) et voir des droits différents.
- [ ] Je peux créer une release avec trois scripts ordonnés, la soumettre, la faire approuver par un autre compte.
- [ ] L'auteur ne peut pas approuver sa release, et c'est testé.
- [ ] L'API renvoie les releases et applique les mêmes règles.
- [ ] Le `chemin_secret` est stocké, pas un mot de passe.
- [ ] Les tests passent.

## 11. Ce que tu laisses de côté volontairement

Pas d'exécution de SQL, pas de planification, pas de Vault, pas de design soigné, pas de déploiement. Les phases suivantes s'en occupent, et vouloir tout faire maintenant te ferait perdre du temps. Savoir délimiter un périmètre est aussi une compétence que Keyes verra d'un bon œil.
