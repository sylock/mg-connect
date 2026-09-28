# Application architecture

Version 0.3 · 28 September 2026. Frontend stack selected by the user; detailed operational choices remain proposals.

## Decision

Use a modular Django monolith with server-rendered HTML. Python is the main language. Tailwind CSS and daisyUI provide the visual system; HTMX updates HTML fragments. Small plain-JavaScript modules handle installation hints and browser-only interactions. PostgreSQL stores shared data. The browser or installed PWA is the client; Django is the authoritative server. Rendering HTML over HTTPS is a client/server architecture even without a separate REST API.

Django is suitable because the application is mostly authenticated forms, permissions, approvals and reports. Its built-in authentication covers accounts, groups, permissions and cookie sessions. Record-level policies, throttling and workflow invariants remain application responsibilities. Use a maintained 5.2 LTS patch and a compatible supported Python release, verified when building; lock exact dependencies then.

## Runtime boundaries

| Component | Responsibility |
| --- | --- |
| Browser / installed PWA | Responsive screens, validated input hints, proof file selection, installation UI. |
| HTTPS reverse proxy, proposed Caddy | TLS, request-size limits, public static assets, proxying Django; no public private-media directory. |
| Django application, proposed Gunicorn process | Sessions, permissions, forms, domain services, HTML rendering, reports and authorised evidence streaming. |
| PostgreSQL | Persistent relational data, constraints, transactional integrity. |
| Private media volume | Evidence bytes addressed by opaque identifiers, accessible through authenticated application routes. |

One application service, one database and one proxy are enough. No Redis, Celery, Kubernetes, object-store subscription or separate frontend application server. A small Tailwind CLI CSS build is now required, superseding the earlier no-frontend-build default. Docker Compose or compatible OCI tooling is a deployment proposal; document a direct Linux alternative if needed.

## Suggested application modules

`accounts`, `achievements`, `attendance`, `leave`, `planning`, `reporting`, `audit`, with a small `config` package and shared templates/static assets. This is logical separation inside one process, not separate services. Create modules incrementally.

Domain services handle create/approve/reject/correct/cancel in transactions. Query/report services have no side effects. The same reporting calculation functions serve desktop and mobile pages. Model forms validate input; database constraints enforce key invariants independently.

## HTTP contracts to implement

Names below are design proposals, not implemented APIs. All paths except sign-in, public static assets, manifest and generic offline page require authentication.

| Method and route | Behaviour and access |
| --- | --- |
| GET/POST `/login/`, POST `/logout/` | Django session login/logout. |
| GET `/` | Own current attendance state and quick actions. |
| GET/POST `/achievements/new/` | Self submission; manager may select beneficiary. |
| GET `/achievements/` | Own entries; managers may inspect all entries. |
| POST `/achievements/<id>/approve/` or `/reject/` | Manager, transaction and expected revision. |
| POST `/achievements/<id>/correct/` or `/void/` | Manager, reason and audit. |
| POST `/attendance/clock-in/` or `/clock-out/` | Self only; idempotency token and server timestamp. |
| GET/POST `/attendance/<employee>/correct/` | Manager, historical correction reason. |
| GET/POST `/leave/new/` | Self only, dates and reason. |
| GET `/leave/` | Own requests; manager can view pending team requests. |
| POST `/leave/<id>/<decision>/` | Explicit approve/reject/withdraw/cancel handlers with role and state validation. |
| GET `/agenda/` | All active users; latest published work and approved leave overlays; managers may explicitly preview drafts. |
| GET `/reports/attendance/`, `/reports/comparison/`, `/reports/achievements/` | All active users; shared date selectors and employee filter, read-only; separate completeness per comparison. |
| GET/POST `/planning/<year>/<month>/` | Manager draft editor; never direct public snapshot edits. |
| POST `/planning/<year>/<month>/publish/` or `/reopen/` | Manager, expected revision, atomic snapshot and audit. |
| GET/POST `/management/holidays/` | Manager selects suggested dates/application/replacements. |
| POST `/planning/events/<id>/comments/` and `/planning/day-comments/` | Manager authoring; server-enforced visibility. |
| GET `/evidence/<id>/` | Beneficiary or manager only; private no-store response. |
| GET/POST `/management/users/` and `/management/schedules/` | Manager workflows through the same audited domain services. |

CSRF on every mutation; never use GET for approval/clocking. Use POST/Redirect/GET for ordinary HTML form submissions. For HTMX submissions return an appropriate HTML fragment or an explicit HTMX redirect; document the response contract and do not send full pages into fragment targets. Return 403 for forbidden operations, suitable validation messages for invalid forms, and 409 for stale decisions/conflicts. Include record revisions in mutation forms. Avoid both managers approving stale copies. Do not expose private data in error responses.

## Authentication and access

Manager-created accounts, no public registration. Bootstrap the first manager through a local management command. Proposed password recovery is manager-issued single-use reset tokens with expiry, delivered outside the app; never log reusable passwords. Email integration is deferred. Add login throttling with a maintained compatible package or proxy/app mechanism and test it.

Use secure HttpOnly SameSite session cookies, HTTPS, correct trusted hosts/origins and CSRF middleware. Limit database privileges and avoid exposing the database port publicly. UI role checks supplement, not replace, server checks.

## PWA and network behaviour

- Responsive HTML using the shared Tailwind/daisyUI theme in UI_GUIDELINES.md, viewport metadata, accessible mobile controls and a French interface.
- `manifest.webmanifest`: stable id, name, short_name, start_url, scope, standalone display, theme/background colours, 192 px and 512 px icons, including a maskable asset if supplied.
- Serve via HTTPS in production. Localhost is a development exception, not a mobile deployment strategy.
- Installation instructions for Android Chrome and iPhone Safari; show the app's install button only when the browser supports the install event. Do not promise the same prompt everywhere.
- A small service worker may cache versioned public static assets and a generic offline page only. Installation and offline operation are distinct: a service worker is not universally an installation requirement.
- No caching of authenticated HTML, report responses, proof images or personal JSON in Cache Storage. Set no-store headers for private responses. Do not queue mutations offline.
- On network failure show that the action is not confirmed. Retry with the same idempotency token; reload authoritative state after reconnecting. Never fabricate a successful clock-in.
- Version the static cache, remove obsolete caches on activation and avoid forcing reload during unsaved forms.

## Evidence

Validate decoded image content, allowed formats, dimensions and size; re-encode images to strip unnecessary metadata. Enforce aggregate request limits. Reject active file formats and decompression bombs. Use random storage keys, authenticated download routes and safe content headers. Never make arbitrary outbound HTTP requests to proof URLs. External links use validated HTTP(S) schemes and safe new-tab attributes.

## Delivery and operations

Provide an example environment file, migrations, dependency lock, documented bootstrap, production settings, Compose configuration, persistent volumes and health checks during implementation. No secrets in this documentation bundle. Employee master records may exist before login provisioning. Use latest compatible security patches, then record exact versions; do not invent a running scaffold now.

Back up PostgreSQL and private media consistently, encrypt backup storage, document retention and restore steps, and verify a restore to a separate instance. Migrations must preserve original time and approval history. Log errors and mutation IDs without passwords, tokens, private leave motives or evidence bytes. A health endpoint exposes no personal data.

Proposed initial responsiveness target: common report requests under two seconds on an agreed small test host with ten synthetic users and one year of data. This is an engineering target to measure, not an observed performance claim.

## References

- https://www.djangoproject.com/download/
- https://docs.djangoproject.com/en/5.2/topics/auth/
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable

Consult the current official deployment/security documentation when implementation starts. No legal compliance or payroll certification is asserted.

## Planning integration (v0.2)

Read PLANNING.md for the authoritative proposed lifecycle. Use a month aggregate with draft editing state and a last-published snapshot pointer. Public queries must read snapshots, not mutable draft event rows. Store publication identifiers in comparison results; compose approved leave as a linked overlay without exposing draft work or comments.

Keep Employee separate from User (optional one-to-one). All employment, contract, attendance, achievement and leave foreign keys reference Employee; author/reviewer references use User. Usual patterns initialise drafts but do not replace contractual baselines.

Holiday generation is local and year-specific. A versioned catalogue supplies proposals; managers configure application. No background scheduler or SaaS is needed. Any chosen library must be pinned, licensed and tested against documented dates.

Use a single global lock order across publication, leave approval/cancellation and planning updates: affected employee rows ordered by ID, then month rows ordered by year/month, then dependent rows. Snapshot validation, activation of manager-draft leave and audit commit atomically. Re-read approved leave after locks; optimistic revision checks prevent stale draft publication. Multi-month operations must not deadlock or leak partial approval. All public event serializers filter private notes before rendering.

## Frontend composition and build

Django renders full pages and reusable partial templates. Use Tailwind utilities for layout and daisyUI components for consistent buttons, badges, inputs, tabs and dialogs. Supply a custom theme from UI_GUIDELINES.md rather than accepting unrelated component defaults. HTMX requests server-rendered fragments for month navigation, filters, request review and forms. Maintain ordinary links/form flows where practical.

Suggested source locations during implementation:

- `templates/base.html`, `templates/components/`, and domain-specific `templates/<module>/` pages/partials.
- `assets/css/app.css` for Tailwind/daisyUI imports and semantic theme tokens.
- `assets/js/` for small installation, dialog and HTMX event handlers.
- `static/dist/` for generated CSS and locally hosted versioned JavaScript.
- `package.json` and a committed lockfile for the CSS build dependencies. A build script uses Tailwind CLI, scans all Django templates and emits minified static CSS before Django static collection.

Verify compatible maintained Tailwind/daisyUI/HTMX releases and lock exact versions at implementation time. Avoid dynamically concatenated CSS class names that cannot be discovered at build time; map event/status names to complete known class strings. No runtime CDN dependency, paid UI kit or commercial scheduling plugin is required. Retain dependency licence notices and document the selected versions.

The development workflow has a CSS watch process alongside Django. Production builds assets once and serves them as static files; no Node process handles user requests. A multi-stage container build may keep Node tooling out of the final Python runtime.

## HTMX response and security contracts

Every HTMX operation uses the same domain services and permissions as its full-page equivalent. POST requests include Django CSRF tokens; file upload forms use multipart encoding with HTMX support. A full-page versus fragment response may share a URL, but must use correct `Vary: HX-Request` semantics and private no-store headers. Do not allow shared caching of authenticated content.

Return field errors in a documented fragment and configure the frontend to render the chosen validation status (for example 422); do not assume HTMX swaps every error response by default. Handle 403, 409 and session expiry explicitly. Redirect an expired session to the complete login screen rather than inserting it into a calendar cell. Keep revision/idempotency tokens in the request across retries.

Disable HTML history caching on authenticated pages. Escape user text; do not execute scripts or HTMX attributes from user comments. Host trusted JavaScript locally. Implement loading and error announcements using accessible live regions, restore keyboard focus after swaps, and prevent fragment listeners from being attached repeatedly. A calendar update must preserve the selected month/employee/date filters.

Frontend references consulted for the selected approach:

- https://tailwindcss.com/docs/installation
- https://daisyui.com/
- https://htmx.org/docs/
