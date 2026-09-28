# Instructions for development agents

## Mission and precedence

Implement the small salon MVP described in `docs/REQUIREMENTS.md`. Read README, requirements, business rules, architecture, data model, planning specification, docs/UI_GUIDELINES.md and acceptance scenarios before changing application code. The user's explicit instructions take precedence. Preserve stable requirement IDs in later iterations. If requirements conflict, surface the conflict rather than silently choosing.

This is a documentation starter, not a running application. Do not claim existing functionality, successful tests, deployment or stakeholder approval without evidence.

## Scope discipline

1. Use the selected Python/Django monolith with PostgreSQL, server-rendered Django templates, Tailwind CSS, daisyUI, HTMX and a lightweight PWA. Explain a necessary departure before making it.
2. Implement all user-requested MVP capabilities in small increments. Do not substitute localStorage demo data for server persistence.
3. No mandatory SaaS, paid API, native app project, microservices, task queue, Kubernetes, payroll integration or separate SPA in the MVP.
4. Keep UI text in French, code and technical docs in English. Keep user-facing screens free of architecture jargon. Apply docs/UI_GUIDELINES.md as the shared visual specification, including responsive planning views.
5. Use open-source dependencies with compatible licences; pin actual resolved versions and document their licences. Never use `latest` as a production image tag.
6. P-labelled business rules are proposed defaults, not validated policy. Keep unknown schedule, holiday and leave settings visible; never invent a contract or silently display an unreliable final balance.

## Implementation boundaries

- Use Django authentication, secure cookie sessions and CSRF protection. No homemade password hashing or JWT-in-localStorage.
- Authorise every request on the server, including reports and evidence downloads. A hidden button is not an access control.
- All authenticated active salon users may view team reports. Do not silently narrow this to self-only. Proposed privacy boundary: leave reasons and correction explanations are available only to the concerned employee and managers.
- Manager is a business group, assignable to multiple users; it is not synonymous with `is_staff` or `is_superuser`.
- Separate acting user from employee concerned. Never impersonate an employee to record on their behalf.
- Put workflow changes in explicit domain services with atomic transactions, audit events and concurrency checks. Keep views thin and reports read-only.
- Use UTC instants plus the Europe/Brussels business timezone, integer seconds for elapsed work and integer minutes for contractual inputs. Avoid floating point arithmetic for durations.
- Version contractual schedules by effective date. Never overwrite past contractual expectations as a side effect of a future schedule change.
- Preserve original clock events. Corrections require a reason and immutable before/after history. No ordinary UI hard deletion of time records.
- Do not credit pending achievements or pending/rejected leave.
- Follow docs/PLANNING.md: contractual baseline, usual patterns, monthly planned events and real attendance are distinct. A draft never alters employee-visible published work. Publication snapshots and approved leave overlays must not overwrite clock records.
- Read shared agenda/actual/comparison reports from the same authorised services. Private reminders and leave reasons must not leak into event titles, HTML attributes or report payloads.
- Reopening a month for draft editing retains its last published snapshot under the proposed rule. Approving leave must not implicitly publish other draft edits.
- Holiday suggestions are year-specific for Belgium/Brussels private-sector context. Keep suggestions separate from manager-selected application and replacement days; selection is not a legal compliance verdict.
- Do not fetch user-provided proof URLs on the server. Validate safe URL schemes and display links safely.
- Validate and privately store images. Never serve uploaded HTML/SVG as evidence or cache private reports in a service worker.
- Keep secrets, real user data, database dumps and uploaded images out of git. Use synthetic fixtures only.

## New feature workflow

When the user asks for a **new specific feature** (not a fix, polish or small adjustment on work already agreed):

1. Create a dedicated git branch from `main` for that feature only.
2. Before writing application code, describe the feature in the requirements documentation under `docs/` (extend `docs/REQUIREMENTS.md` and related docs as needed: business rules, acceptance, planning, data model). Preserve stable requirement IDs.
3. Stop and align with the user on that description. Do not implement until they explicitly agree.
4. After agreement, implement on that branch, iterate with the user, then merge to `main` when they are satisfied.

Do **not** create a new branch for every code change. Branches are for specific new features. Fixes, refinements and follow-ups on an already agreed feature stay on the current feature branch (or on `main` if that work is already merged and the change is not a new feature).

## Work style and verification

Deliver one vertical slice at a time following `docs/IMPLEMENTATION_PLAN.md`. Record actual setup and run commands when they exist. Add migrations with model changes. Reuse one reporting calculation service across all views. Reuse Django template components and semantic theme tokens across all screens.

Test meaningful risks: access control, time and leave arithmetic, date boundaries, concurrent double taps/approvals, audit integrity and private uploads. Run transaction/concurrency tests against PostgreSQL. Do not add tests which only restate implementation details.

Before completion, run relevant tests, migration checks and Django deployment checks; manually verify the complete employee and manager journeys, narrow mobile layouts and PWA installation on actual target browsers when available. If not available, state exactly what was and was not checked. Document backup restoration and demonstrate a restore before live operational use.

Never publish source, invite employees, deploy publicly or send email unless the active task authorises it. Keep development reversible and provide reviewable changes. Do not rewrite these instructions to bypass missing permission or a failing check.

## Frontend implementation rules

- Read UI_GUIDELINES.md before building any user-facing page. Build the actual app interface, not the default Django admin as the employee/manager product.
- Use Tailwind CLI + daisyUI with a committed package lock and compiled local static assets. Node.js is a build-time tool, not another production application service. No browser Tailwind CDN compiler or paid component pack.
- HTMX augments server-rendered forms and fragments. Django remains authoritative for permissions, workflow state, totals and clock acknowledgement. Do not add a separate SPA or duplicate domain calculations in JavaScript.
- Include CSRF tokens on HTMX mutations and explicit handling for validation errors, stale revisions, session expiry and upload failures. Preserve useful inputs on errors.
- Disable HTMX history snapshots for authenticated pages (`hx-history="false"` and/or historyCacheSize 0); private HTML must not enter browser localStorage through HTMX.
- Do not use optimistic success for clocking, leave decisions or publication. Disable duplicate submission while pending and retain server idempotency protection.
- Verify 360 px, 768 px and 1440 px layouts, keyboard flows, focus after fragment swaps, readable contrast and long French labels. Record actual verification limits.
