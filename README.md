# Release Manager

[Lire la documentation en français](README.fr.md)
[Lire la documentation de l'architecture](https://github.com/Y0UBdev/Modular-Monolith-Django-Architecture/blob/main/README.md)

## 1. What you're building

An internal web application where users with **different roles** prepare **releases** (bundles of ordered SQL scripts) intended for a **target database**, and push them through an **approval workflow**.

At the end of phase 1, the application **cannot yet execute** the scripts (that's phase 3). It can, however:

- store environments, target databases, releases and their scripts;
- enforce a workflow (draft → submitted → approved);
- restrict each action according to the user's role;
- expose releases through a REST API.

It's the skeleton everything else will plug into.

## 2. Initial technical choices

| Item | Choice | Why |
|---|---|---|
| Python | 3.12 or later, in a virtual environment (`venv`) | Standard |
| Django | Latest LTS version (5.2) | Stability, it's what a company would choose |
| API | Django REST Framework | Mentioned in the job posting (REST API) |
| Database for now | SQLite | Zero setup. Oracle comes in phase 2 |
| Configuration | Environment variables (`django-environ`) | A habit to build from the start: no secrets in the code |
| Tests | `pytest-django` or Django's `TestCase` | A tool that deploys SQL scripts has to be tested |
| Git | Repository from day one, `.gitignore`, clear commits | Git is in the posting's technology list |

**Warning:** SQLite only backs *your application*. The Oracle database will be the **target** of the scripts, a very different role. Understanding this distinction is important.

## 3. Project structure

```
release_manager/
├── manage.py
├── config/                  # settings, urls, wsgi
├── releases/                # the business core
│   ├── models.py
│   ├── services.py          # workflow logic (transitions)
│   ├── permissions.py       # permission and group names
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

A single business app is enough for now. You'll add another one for auditing in phase 6.

## 4. Data models

### `Environnement` (Environment)
| Field | Type | Note |
|---|---|---|
| `code` | CharField, unique | `TEST`, `ACC`, `PROD` |
| `nom` | CharField | |
| `approbation_requise` | BooleanField | True for production |
| `ordre` | PositiveInteger | For sorting: test, then acceptance, then production |

### `BaseCible` (Target database)
| Field | Type | Note |
|---|---|---|
| `nom` | CharField | Readable name |
| `environnement` | ForeignKey | |
| `type_sgbd` | CharField with choices | Only one value for now: `ORACLE`. This field prepares for supporting other DBMSs |
| `dsn` | CharField | Address / service name |
| `chemin_secret` | CharField | **The path of the secret in Vault, never the password.** Prepares phase 5 |
| `active` | BooleanField | |

### `Release`
| Field | Type | Note |
|---|---|---|
| `titre` | CharField | |
| `description` | TextField | |
| `base_cible` | ForeignKey | |
| `auteur` | ForeignKey to `User` | |
| `statut` | CharField with choices | See workflow below |
| `approuvee_par` | ForeignKey to `User`, nullable | |
| `approuvee_le` | DateTimeField, nullable | |
| `planifiee_le` | DateTimeField, nullable | Will be used in phase 4 |
| `cree_le` / `modifie_le` | Automatic DateTimeFields | |

### `Script`
| Field | Type | Note |
|---|---|---|
| `release` | ForeignKey | |
| `ordre` | PositiveInteger | Unique per release (`unique_together` or `UniqueConstraint`) |
| `nom` | CharField | E.g. `001_create_table_facture.sql` |
| `contenu` | TextField | The SQL |
| `contenu_retour_arriere` | TextField, blank allowed | The rollback script, written in advance |
| `hash_contenu` | CharField | SHA-256 of the content, computed on save. Later used to prove what was executed |

The `Execution` model (status, start, end, output, error per script) comes in phase 3. Don't create it now.

## 5. The workflow to implement

**Statuses:** `BROUILLON` (draft) → `SOUMISE` (submitted) → `APPROUVEE` (approved), with two possible exits: `REFUSEE` (rejected) and `ANNULEE` (cancelled). The later statuses (`PLANIFIEE`, `EN_COURS`, `TERMINEE`, `ECHEC`) will be added in phases 3 and 4. You can declare them in the choices now if you like, but don't implement their transitions.

| Action | From | To | Who can do it |
|---|---|---|---|
| Submit | Draft | Submitted | The release's author |
| Approve | Submitted | Approved | An approver, **different from the author** |
| Reject | Submitted | Rejected | An approver |
| Cancel | Draft, Submitted | Cancelled | The author |
| Edit scripts | Draft only | , | The author |

**Business rules to code and test:**

1. **Separation of duties**: nobody approves their own release. It's a classic audit rule, and it will go over very well in an interview.
2. **A submitted or approved release can no longer be edited.** Otherwise someone could get a script approved and then change its content.
3. **A release with no scripts cannot be submitted.**
4. **Invalid transitions raise a clear error** (for example, approving a draft).
5. Environments with `approbation_requise = False` could allow a shortcut: decide on it and document it.

**Good practice to adopt:** put the logic in functions in `services.py` (for example `soumettre(release, utilisateur)`), not in the views. The views, the admin and the API will all call the same functions. It's *Single Responsibility* in practice, and it's easy to test.

## 6. Roles and permissions

Four Django groups, created by a data migration or a management command:

| Group | Can |
|---|---|
| **Reader** (Lecteur) | View releases |
| **Author** (Auteur) | Reader + create and edit own drafts, submit |
| **Approver** (Approbateur) | Reader + approve or reject |
| **Executor** (Exécutant) | Reader + (later) schedule and launch |

Use Django's **custom permissions** mechanism (`Meta.permissions`, for example `approuver_release`) rather than testing group names in the code. You check "does the user have the permission?", not "are they in the group?". It's cleaner and more flexible.

## 7. Screens and API

**Django admin** (quick, serves as a back office):
- Environments and target databases managed here.
- Releases with their scripts as *inlines*.
- Filters by status and by environment.

**Custom pages** (minimum):
- Release list with filters (status, environment).
- Release detail: information, scripts in order, action buttons visible only if the user has the right to use them.
- Draft creation and editing.
- Login and logout.

**REST API (DRF)**, deliberately minimal:
- `GET /api/releases/` and `GET /api/releases/{id}/`
- `POST /api/releases/{id}/soumettre/`, `/approuver/`, `/refuser/`
- Session authentication to start with, with the same permissions as the interface.

## 8. Tests to write

You don't need full coverage, but these cases must exist:

- An author cannot approve their own release.
- A release with no scripts cannot be submitted.
- A script cannot be edited after submission.
- A reader cannot submit or approve.
- An invalid transition is refused.
- A script's hash changes when its content changes.

## 9. Two-day schedule

**Day 1: foundations**
1. Git repository, virtual environment, Django project, `requirements.txt`, `.gitignore`, `.env.example`.
2. Models + migrations.
3. Configured admin (inlines, filters).
4. Groups and permissions created automatically.
5. Sample dataset (a command that creates environments, a target database and a release).

**Day 2: logic and access**
1. `services.py` with the transitions and their rules.
2. Tests for those rules.
3. List, detail and creation views, with permission checks.
4. Minimal DRF API.
5. README (how to run, model diagram, workflow) and a clean commit.

## 10. Success criteria

You've finished phase 1 when:

- [ ] I can run the project by following your README alone.
- [ ] I can log in with three accounts (author, approver, reader) and see different rights.
- [ ] I can create a release with three ordered scripts, submit it, and have another account approve it.
- [ ] The author cannot approve their own release, and it's tested.
- [ ] The API returns the releases and applies the same rules.
- [ ] The `chemin_secret` is stored, not a password.
- [ ] The tests pass.

## 11. What you deliberately leave out

No SQL execution, no scheduling, no Vault, no polished design, no deployment. The following phases cover those, and trying to do everything now would waste your time. Knowing how to define a scope is also a skill Keyes will appreciate.