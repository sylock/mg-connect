# Salon Team — development starter

Version: 0.3 · 28 September 2026 · Working project name

Specifications plus an in-progress Django application (slice 1 foundation on `feature/foundation`). Start with `AGENTS.md` and `docs/PROGRESS.md`. Formal documents and code identifiers are in English; the user interface is in French.

## Local setup (foundation)

Requires Python 3.12+ (3.13 preferred; 3.14 works with current pins), Node.js 20+ for the CSS build, and PostgreSQL 16 (recommended).

```bash
# Python venv — never install project deps on system Python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.lock.txt

# CSS build (committed output also lives in static/dist/)
npm ci
npm run build:css

cp .env.example .env
# Start Postgres, e.g.: docker compose up -d db
python manage.py migrate
python manage.py bootstrap_manager --username manager --password 'choose-a-secret' --display-name 'Gérant'
python manage.py runserver
```

If PostgreSQL is not available yet, temporary local-only escape hatch:

```bash
USE_SQLITE=true python manage.py migrate
USE_SQLITE=true python manage.py runserver
```

Do not use `USE_SQLITE` for production or concurrency tests. Automated access-control tests use in-memory SQLite via `config.settings.test`:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test accounts.tests
```

Open http://127.0.0.1:8000/login/ — French shell, Accueil / Agenda / Gestion (managers).

Dependency licence inventory: [docs/DEPENDENCY_NOTICES.md](docs/DEPENDENCY_NOTICES.md).

## Goal

Build a small, self-hostable, open-source application for a salon: record employee achievements, approve evidence, clock attendance, request leave, prepare and publish monthly team schedules, and share on-screen reports. No mandatory paid SaaS, per-user licence, commercial identity provider or app-store account. Hosting, a domain, maintenance and backups may still incur costs.

## Proposed technology

- Python + Django 5.2 LTS in a project **`.venv`**, latest compatible security patch at implementation time.
- Django templates + Tailwind CSS + daisyUI for a colourful, responsive interface.
- HTMX for partial-page interactions; small amounts of plain JavaScript for PWA and browser-only behaviours.
- A local CSS build using the Tailwind CLI and locked npm dependencies; no Node.js application server.
- PostgreSQL for development, tests involving transactions, and production.
- Progressive Web App (PWA): one website, installable from a supported mobile browser.
- A single Django deployment behind an HTTPS reverse proxy, with private persistent evidence storage.
- MIT licence, selected as a simple permissive default for this starter and future project contributions. See `LICENSE`. This is a proposed project licensing choice, not a licence granted over any third-party material.

Django supplies accounts, sessions, groups and permissions. Domain rules, record-level access and login rate limits still need implementation. A separate SPA, native Android/iOS projects and public REST API are not needed for this MVP.

## Read in order

| File | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions for the development AI. |
| [docs/PROGRESS.md](docs/PROGRESS.md) | Living implementation status, gates and history (resume here). |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Scope, roles and traceable requirements. |
| [docs/PLANNING.md](docs/PLANNING.md) | Monthly planning, publication, holiday proposals, agenda events and comments. |
| [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md) | Workflows, reporting calculations and provisional business choices. |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technology, boundaries, deployment and PWA behaviour. |
| [docs/UI_GUIDELINES.md](docs/UI_GUIDELINES.md) | Required visual design, colours, components and responsive behaviour. |
| [docs/DATA_MODEL.md](docs/DATA_MODEL.md) | Initial logical model and integrity constraints. |
| [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md) | Concrete acceptance scenarios, including calculation examples. |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Small delivery increments and completion checks. |

## What a PWA means — explanation for the salon

Une PWA est un site web prévu pour fonctionner comme une petite application. On ouvre son adresse HTTPS sur le téléphone, puis on l’ajoute à l’écran d’accueil. Elle dispose de son icône et peut s’ouvrir dans une fenêtre dédiée. Sur Android, utiliser par exemple Chrome et son option d’installation ; sur iPhone, ouvrir le site dans Safari puis utiliser le menu de partage et « Sur l’écran d’accueil ». Les libellés varient selon la version.

Le serveur conserve les données communes. Le téléphone ne contient pas une seconde base à synchroniser. La première version demande une connexion Internet pour pointer, enregistrer un succès ou demander un congé. Installer l’application ne signifie donc pas pouvoir travailler hors connexion. Une mise à jour du site met aussi à jour l’application, sans publication sur un store.

## Status and assumptions

User instructions are recorded as U requirements. P requirements and architecture choices are explicit proposals that make the first implementation concrete. They must not be presented as owner-approved policies. Develop with these visible defaults; ask targeted questions when a real calculation needs missing contractual information. Do not block unrelated implementation.

No actual employee roster, schedules, absence rules, hosting credentials or repository has been supplied. Do not populate real operational data from memory or invent it. All example data must be labelled synthetic.

## Sources

- User discussion of 25 and 28 September 2026: achievements, manager approval, open source, shared reports, attendance and leave.
- [Django support/download information](https://www.djangoproject.com/download/).
- [Django authentication](https://docs.djangoproject.com/en/5.2/topics/auth/).
- [MDN: Making PWAs installable](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable).
- [Connecteam: form manager fields](https://help.connecteam.com/en/articles/6867498-how-to-add-manager-fields-to-a-form), functional inspiration only.
- Method: BABOK v3 §7.2 and The Business Analysis Standard v2.0 §5.5, consulted through the supplied documentary knowledge bases. Specifications are reviewed drafts, not stakeholder-approved or implemented requirements.

Connecteam is inspiration for workflow concepts only. Do not copy its source code, brand, visual assets or proprietary interface.

## Revision 0.2

Monthly planning is now in MVP, replacing its previous deferral. Keep contractual schedules, usual weekly patterns, published monthly plans and actual attendance distinct. Three views are required: shared agenda, actual attendance report and planned-versus-actual comparison. Approved leave updates the agenda through a linked overlay; general event comments and private reminders have explicit visibility. Existing requirement IDs are preserved.

## Revision 0.3 and how to start

This complete package includes the monthly planning scope from v0.2 and the accepted frontend direction: Django templates, Tailwind CSS, daisyUI and HTMX, with a colourful mobile-first PWA. It replaces the earlier plain-CSS/frontend direction; it does not replace the backend or remove planning features.

Extract the archive, then put the contents of `salon-team-starter/` at the repository root. `AGENTS.md` must be at that root, alongside this README and the `docs/` folder. Open that repository in the development agent. Codex recognises AGENTS.md; other agents may require an explicit instruction or their own entry file. Do not assume every AI tool automatically loads every Markdown file.

Suggested initial instruction: “Read AGENTS.md and the documents it references, including PLANNING.md and UI_GUIDELINES.md. Implement the plan in reviewable increments, preserving all MVP requirements.”

The package is a specification starter with eleven files, not runnable application code. The visual palette and component rules are implementation guidance; the remaining contractual and publication policy assumptions stay labelled as proposals.
