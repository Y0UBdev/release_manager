# Architecture Django Monolithe Modulaire

Template de démarrage pour développer des applications web avec **Django, Django REST Framework, React et TypeScript**.

Ce template fournit une structure organisée, modulaire et évolutive, conçue pour séparer les responsabilités du backend, du frontend, de la logique métier et de l'accès aux données.

L'objectif est de pouvoir démarrer différents projets sans devoir redéfinir leur architecture à chaque fois.

## Table des matières

- [Présentation](#présentation)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Responsabilités des couches](#responsabilités-des-couches)
- [Configuration et installation](#configuration-et-installation)
- [Utilisation du template GitHub](#utilisation-du-template-github)
- [Cloner le dépôt](#cloner-le-dépôt)
- [Créer une application Django](#créer-une-application-django)
- [Conventions de développement](#conventions-de-développement)
- [Tests](#tests)
- [Bonnes pratiques](#bonnes-pratiques)

---

## Présentation

Ce dépôt constitue une base réutilisable pour développer des applications web, notamment :

- Applications de gestion et outils internes.
- API REST.
- Applications web avec une interface React.
- Applications métier avec plusieurs modules fonctionnels.
- Projets nécessitant une séparation claire entre la présentation, la logique métier et l'accès aux données.

### Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python | Langage du backend |
| Django | Framework backend et ORM |
| Django REST Framework | Création d'API REST |
| React | Bibliothèque frontend |
| TypeScript | Typage statique du frontend |
| Vite | Serveur de développement et outil de build |
| Git | Gestion de versions |

## Architecture

### Nom de l'architecture

**Modular Monolith — Architecture en couches**

Le projet adopte une architecture monolithique modulaire : le backend Django est une application unique, organisée en modules métier distincts.

Le code est séparé selon ses responsabilités afin de limiter le couplage et de faciliter les évolutions.

Cette organisation s'inspire de principes de séparation des responsabilités présents dans les architectures en couches et la Clean Architecture, sans imposer une séparation stricte entre domaine, application et infrastructure.

### Principes fondamentaux

1. **Séparation des responsabilités** : chaque fichier et chaque module ont un rôle identifiable.
2. **Modularité** : chaque application Django regroupe une fonctionnalité métier cohérente.
3. **Centralisation de la configuration** : les paramètres sont regroupés dans `config/`.
4. **Séparation du frontend et du backend** : React et Django disposent de leurs propres dépendances et commandes.
5. **Évolutivité** : les couches supplémentaires sont introduites lorsque leur complexité le justifie.

### Flux général d'une requête API

```text
Frontend React
      |
      | Requête HTTP / JSON
      v
config/urls.py
      |
      v
apps/<module>/urls.py
      |
      v
views.py
      |
      v
serializers.py
      |
      v
services.py -------- queries.py
      |                   |
      v                   v
   models.py          Django ORM
      |                   |
      +---------+---------+
                |
                v
           Base de données
```

Ce schéma représente un flux possible, et non une obligation pour chaque requête. Une vue peut appeler directement un serializer ou une query lorsqu'aucun service métier n'est nécessaire.

---

## Structure du projet

```text
project-root/
├── .env.example
├── .gitignore
├── manage.py
├── README.md
│
├── apps/
│   └── <app_name>/
│       ├── __init__.py
│       ├── apps.py
│       ├── admin.py
│       ├── models.py
│       ├── queries.py
│       ├── serializers.py
│       ├── services.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       └── tests/
│           ├── __init__.py
│           ├── test_models.py
│           ├── test_queries.py
│           └── test_services.py
│
├── common/
│   └── __init__.py
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── docs/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── scripts/
│
└── web/
    ├── .gitignore
    ├── eslint.config.js
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    ├── tsconfig.app.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── assets/
        │   ├── images/
        │   └── styles/
        │       └── global.css
        ├── components/
        ├── hooks/
        └── types/
```

> Remarque : cette arborescence est un modèle de référence. Si `config/settings/` est utilisé comme package Python, il ne peut pas coexister avec un fichier `config/settings.py` sur le même système de fichiers. Il faut donc conserver une seule de ces deux formes. Dans ce template, la configuration par environnement est organisée dans `config/settings/`.

De même, `apps/<app_name>/apps.py` doit être ajouté s'il est absent, car il permet de déclarer la configuration de l'application Django.

---

## Responsabilités des couches

### 1. `apps/` — Applications métier

Ce dossier contient les modules fonctionnels de l'application.

Exemples :

- `users/` : gestion des utilisateurs et profils.
- `projects/` : gestion des projets.
- `tasks/` : gestion des tâches.
- `documents/` : gestion des documents.

Chaque application regroupe les éléments nécessaires à sa fonctionnalité : modèles, vues, routes, validation, logique métier et tests.

Une application doit représenter une responsabilité fonctionnelle cohérente, et non une couche technique commune à tout le projet.

### 2. `models.py` — Modèles de données

Définit les modèles Django, leurs champs, leurs relations et leurs comportements liés aux données.

Responsabilités :

- Définir la structure des données.
- Déclarer les relations entre les entités.
- Définir les contraintes et validations liées aux modèles.
- Fournir les objets utilisés par l'ORM Django.

Les modifications de modèles peuvent nécessiter la création de migrations.

### 3. `queries.py` — Lecture des données

Regroupe les opérations de lecture réutilisables lorsque leur centralisation est utile.

Exemples :

- Rechercher des projets.
- Récupérer les projets d'un utilisateur.
- Filtrer des éléments selon leur statut.
- Effectuer des lectures avec jointures, annotations ou agrégations.

Les queries utilisent généralement l'ORM Django.

Elles ne doivent pas devenir un simple intermédiaire obligatoire pour chaque accès à la base de données. Une requête simple peut rester directement dans une vue ou un service si cela demeure clair.

### 4. `services.py` — Logique métier

Contient les opérations métier qui coordonnent plusieurs étapes ou objets.

Exemples :

- Créer un projet en vérifiant certaines conditions.
- Affecter une tâche à un utilisateur après vérification des permissions métier.
- Modifier plusieurs objets au cours d'une même opération.
- Orchestrer une transaction ou une intégration externe.

Les services ne doivent pas contenir de logique HTTP spécifique, comme la construction d'une réponse JSON ou la lecture directe des paramètres d'une requête.

Une opération CRUD simple ne nécessite pas obligatoirement un service dédié.

### 5. `serializers.py` — Sérialisation et validation API

Utilisé principalement avec Django REST Framework.

Responsabilités :

- Convertir les objets Django en données exploitables par le frontend.
- Valider les données reçues depuis les requêtes API.
- Contrôler les champs exposés par l'API.
- Transformer les données entrantes en valeurs validées.

Les serializers ne doivent pas remplacer la couche de services pour les workflows métier complexes.

### 6. `views.py` — Endpoints et traitement HTTP

Les vues constituent le point d'entrée des requêtes HTTP dans l'application.

Responsabilités :

- Recevoir les requêtes.
- Utiliser les serializers pour valider les données lorsque nécessaire.
- Appeler les services ou queries appropriés.
- Retourner une réponse HTTP, HTML ou JSON selon le type de vue.

Avec Django REST Framework, les vues peuvent être basées sur `APIView`, des vues génériques ou des `ViewSet`.

### 7. `urls.py` — Routage

Associe les chemins HTTP aux vues correspondantes.

Chaque application possède son propre `urls.py` pour ses routes métier. Le fichier `config/urls.py` rassemble les routes principales et inclut celles des applications.

Exemple de routes :

```text
/api/projects/
/api/projects/42/
/api/users/
```

Le routage ne contient pas la logique métier : il détermine quelle vue doit traiter la requête.

### 8. `admin.py` — Administration Django

Configure l'affichage et la gestion des modèles dans l'interface d'administration Django.

Il permet notamment de rechercher, filtrer, consulter et modifier les données depuis l'administration, selon les permissions accordées.

### 9. `migrations/` — Évolution du schéma de base de données

Contient les migrations générées par Django pour suivre les changements apportés aux modèles.

Commandes usuelles :

```bash
python manage.py makemigrations
python manage.py migrate
```

Les migrations doivent être versionnées dans Git.

### 10. `tests/` — Tests automatisés

Contient les tests de l'application.

Convention proposée :

- `test_models.py` : comportement des modèles et contraintes.
- `test_queries.py` : résultats des lectures et filtres.
- `test_services.py` : règles métier et opérations.
- `test_views.py` : endpoints, réponses HTTP et permissions, si nécessaire.

Les fichiers de tests doivent suivre les responsabilités réelles de l'application. Il n'est pas nécessaire de conserver des fichiers de tests vides.

---

## Configuration globale

### `config/`

Contient la configuration centrale du projet Django.

#### `config/settings/`

Organise les paramètres selon l'environnement d'exécution.

| Fichier | Responsabilité |
|---|---|
| `base.py` | Paramètres communs à tous les environnements |
| `development.py` | Paramètres de développement local |
| `production.py` | Paramètres de production |
| `test.py` | Paramètres adaptés aux tests |
| `__init__.py` | Initialisation éventuelle du package |

Le module de paramètres actif est choisi à l'aide de la variable `DJANGO_SETTINGS_MODULE`.

Exemples :

```text
config.settings.development
config.settings.production
config.settings.test
```

La configuration effective doit être cohérente avec la manière dont `manage.py`, ASGI et WSGI sélectionnent les paramètres.

#### `config/urls.py`

Déclare les routes globales du projet, notamment l'administration Django et les préfixes des différentes applications.

#### `config/asgi.py`

Expose l'application Django au moyen de l'interface ASGI, utilisée par les serveurs compatibles et certaines applications asynchrones.

#### `config/wsgi.py`

Expose l'application Django au moyen de l'interface WSGI, utilisée par de nombreux serveurs de déploiement traditionnels.

### `manage.py`

Point d'entrée des commandes d'administration Django.

Exemples :

```bash
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
python manage.py test
```

### `.env.example`

Documente les variables d'environnement nécessaires au fonctionnement du projet.

Exemple :

```dotenv
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Ce fichier est un modèle : les noms doivent correspondre à ceux réellement utilisés par les paramètres Django.

Le fichier `.env` local doit contenir les valeurs effectives et ne doit pas être commité. Il faut également prévoir un mécanisme de chargement des variables d'environnement si le projet en nécessite un.

### `.gitignore`

Exclut du dépôt les fichiers générés, les environnements virtuels, les secrets, les caches et les dépendances installées localement.

### `common/` — Code transversal

Réservé aux éléments réellement partagés par plusieurs applications.

Exemples éventuels :

- Exceptions communes.
- Utilitaires génériques.
- Constantes transversales.

Éviter d'y placer du code uniquement parce qu'il ne trouve pas de place ailleurs. Une fonctionnalité propre à une application doit rester dans cette application.

### `docs/` — Documentation technique

Contient la documentation complémentaire du projet.

Exemples :

- Décisions d'architecture.
- Documentation de l'API.
- Instructions de déploiement.
- Procédures de développement.
- Schémas techniques.

### `requirements/` — Dépendances Python

Les dépendances sont organisées par environnement.

| Fichier | Contenu attendu |
|---|---|
| `base.txt` | Dépendances communes du backend |
| `development.txt` | Outils supplémentaires pour le développement |
| `production.txt` | Dépendances propres au déploiement, si nécessaire |

Les fichiers spécifiques peuvent référencer `base.txt` avec une directive `-r base.txt`.

### `scripts/` — Scripts auxiliaires

Réservé aux scripts d'automatisation, d'importation de données ou de maintenance ponctuelle.

Les opérations récurrentes qui doivent utiliser le contexte Django sont généralement mieux placées dans des commandes personnalisées `management/commands/`.

---

## Frontend React

Le dossier `web/` constitue le projet frontend. Il dispose de ses propres dépendances, de son propre environnement de développement et de sa propre commande de build.

### `web/src/main.tsx`

Point d'entrée de l'application React. Il initialise l'interface et monte le composant racine dans le document HTML.

### `web/src/assets/`

Contient les ressources statiques utilisées par le frontend.

- `images/` : images, illustrations et autres ressources graphiques.
- `styles/global.css` : styles globaux de l'application.

### `web/src/components/`

Contient les composants d'interface réutilisables, par exemple les boutons, modales, champs de formulaire et éléments de navigation.

Les composants fortement liés à une fonctionnalité peuvent être regroupés dans un dossier `features/` si le frontend devient plus important.

### `web/src/hooks/`

Contient les hooks React personnalisés, destinés à encapsuler une logique réutilisable liée à React.

### `web/src/types/`

Contient les types TypeScript partagés dans le frontend, lorsque leur réutilisation le justifie.

### `web/public/`

Contient les ressources statiques servies telles quelles par Vite, sans traitement habituel par le graphe d'importation.

### `web/index.html`

Document HTML d'entrée utilisé par Vite pour démarrer l'application frontend.

### `web/package.json`

Déclare les dépendances JavaScript, les métadonnées et les scripts du projet.

### `web/package-lock.json`

Verrouille les versions résolues des dépendances npm pour rendre les installations reproductibles.

### `web/vite.config.ts`

Configure Vite, notamment le serveur de développement, les plugins et la compilation frontend.

### `web/tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`

Configurent TypeScript pour le projet et ses différents contextes de compilation.

### `web/eslint.config.js`

Configure ESLint pour détecter les problèmes et appliquer les conventions de qualité du code.

### `web/.gitignore`

Définit les exclusions spécifiques au frontend, en complément du `.gitignore` racine.

---

## Installation et configuration

### Prérequis

Installer les outils suivants :

- Python dans une version compatible avec les dépendances du projet.
- Node.js dans une version compatible avec Vite et les dépendances React.
- npm, fourni avec Node.js.
- Git.

### 1. Cloner le dépôt

```bash
git clone <REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
```

### 2. Créer un environnement Python

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Sous Linux ou macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances backend

Pour le développement :

```bash
python -m pip install -r requirements/development.txt
```

Cette commande suppose que `development.txt` référence les dépendances communes de `base.txt`.

### 4. Configurer les variables d'environnement

Copier `.env.example` vers `.env`, puis renseigner les valeurs nécessaires.

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Vérifier que Django charge effectivement ces variables selon la configuration du projet.

Ne jamais publier de clé secrète ou de mot de passe dans Git.

### 5. Préparer la base de données

```bash
python manage.py migrate
```

Créer un compte administrateur si nécessaire :

```bash
python manage.py createsuperuser
```

### 6. Démarrer le backend

```bash
python manage.py runserver
```

Par défaut, le serveur de développement Django est accessible à l'adresse :

`http://127.0.0.1:8000/`

### 7. Installer les dépendances frontend

Dans un autre terminal :

```bash
cd web
npm ci
```

### 8. Démarrer React

```bash
npm run dev
```

Vite affiche l'adresse locale à laquelle le frontend est accessible, généralement :

`http://localhost:5173/`

Le frontend doit être configuré pour communiquer avec l'API Django. En développement, cela peut passer par une URL d'API explicite ou par un proxy Vite. Si les deux serveurs utilisent des origines différentes, il faut également configurer correctement CORS côté Django.

---

## Utilisation du template GitHub

Si le dépôt est configuré comme un **GitHub Template Repository**, il est possible de créer directement un nouveau dépôt à partir de cette structure.

### Méthode 1 — Utiliser le bouton « Use this template »

1. Ouvrir le dépôt du template sur GitHub.
2. Cliquer sur **Use this template**.
3. Sélectionner **Create a new repository**.
4. Choisir le propriétaire, le nom et la visibilité du nouveau dépôt.
5. Créer le dépôt.
6. Cloner le nouveau dépôt sur la machine locale.

```bash
git clone <NEW_REPOSITORY_URL>
cd <NEW_REPOSITORY_DIRECTORY>
```

Cette méthode crée un nouveau dépôt basé sur le contenu du template, sans reprendre son historique Git comme un fork classique.

### Méthode 2 — Cloner directement le dépôt

```bash
git clone <TEMPLATE_REPOSITORY_URL>
cd <TEMPLATE_REPOSITORY_DIRECTORY>
```

Cette méthode est adaptée pour tester ou développer le template lui-même.

Si le but est de démarrer un projet indépendant, il faut configurer un nouveau dépôt distant ou créer le projet via la fonctionnalité de template GitHub, plutôt que de continuer à pousser les changements vers le dépôt source.

### Adapter le template au nouveau projet

Après la création du dépôt :

1. Renommer le dossier `apps/<app_name>/` pour lui donner un nom métier pertinent.
2. Adapter la configuration Django au projet.
3. Ajouter les dépendances réellement nécessaires.
4. Configurer les variables d'environnement.
5. Créer les applications métier nécessaires.
6. Configurer les URL globales et les routes des applications.
7. Adapter le frontend React et l'URL de l'API.
8. Mettre à jour ce README avec les informations spécifiques au projet.

---

## Créer une application Django

Chaque fonctionnalité métier doit être représentée par une application Django lorsque cela apporte une séparation cohérente.

Exemple : créer une application `projects`.

Depuis la racine du dépôt :

```bash
python manage.py startapp projects apps/projects
```

Vérifier que la commande a bien généré les fichiers dans le dossier cible. Si la version de Django utilisée ne prend pas en charge cette forme de commande, créer l'application dans un dossier temporaire puis déplacer ses fichiers.

La structure attendue est :

```text
apps/
└── projects/
    ├── __init__.py
    ├── apps.py
    ├── admin.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── migrations/
    └── tests/
```

Ajouter ensuite l'application dans `INSTALLED_APPS`, avec un chemin Python cohérent avec l'organisation du projet. Par exemple, `apps.projects` peut être utilisé si le package racine `apps` est importable et si `apps.py` est correctement configuré.

Ajouter les fichiers `queries.py`, `services.py` et `serializers.py` lorsque les besoins de l'application le justifient.

Enfin, enregistrer ses routes dans `config/urls.py` en utilisant `include()`.

---

## Conventions de développement

### Séparation des responsabilités

- Les vues gèrent les requêtes et réponses HTTP.
- Les serializers valident et représentent les données de l'API.
- Les services orchestrent les opérations métier.
- Les queries centralisent les lectures réutilisables.
- Les modèles Django représentent les données et leurs relations.
- La configuration globale reste dans `config/`.

### Ne pas multiplier les couches inutilement

Les fichiers `services.py`, `queries.py` et `serializers.py` sont des conventions d'organisation, pas des obligations pour chaque application.

Une opération simple peut utiliser directement l'ORM. Introduire une abstraction supplémentaire uniquement si elle améliore réellement la lisibilité, la réutilisation, les tests ou le découplage.

### Variables d'environnement

- Ne jamais commiter le fichier `.env`.
- Fournir un `.env.example` documenté.
- Ne pas utiliser `DEBUG=True` en production.
- Utiliser une clé secrète robuste et des hôtes autorisés correctement configurés.

### Frontend et backend

- Garder les dépendances Python dans les fichiers `requirements/`.
- Garder les dépendances JavaScript dans `web/package.json`.
- Utiliser `npm ci` pour les installations reproductibles en CI.
- Centraliser la configuration de l'URL de l'API côté frontend plutôt que de la disperser dans les composants.

---

## Tests

Exécuter les tests Django :

```bash
python manage.py test
```

Exécuter les tests d'une application particulière :

```bash
python manage.py test apps.projects
```

La suite de tests peut être complétée avec des tests d'intégration API et des tests frontend selon les besoins du projet.

Pour le frontend, les commandes disponibles dépendent des scripts définis dans `web/package.json`.

---

## Bonnes pratiques

- Privilégier des applications métier cohérentes et faiblement couplées.
- Conserver les migrations dans le dépôt.
- Documenter les variables d'environnement.
- Ne pas placer les règles métier dans les vues.
- Éviter de transformer `common/` en dossier fourre-tout.
- Réserver `infrastructure/` aux intégrations techniques ou abstractions réellement nécessaires.
- Ajouter une documentation dans `docs/` lorsque les choix d'architecture ou les procédures deviennent complexes.
- Adapter la structure aux besoins réels plutôt que de créer tous les dossiers à l'avance.

---

**Objectif du template :** fournir un socle cohérent, compréhensible et maintenable pour démarrer rapidement des projets Django + React, tout en permettant à chaque projet d'évoluer selon ses besoins propres.
