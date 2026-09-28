# Implementation progress

Living status for any agent or human resuming work. Delivery order stays in [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md). Update this file after meaningful work, end of session, or gate decisions. Do not mark a slice `done` without recorded evidence.

Status values: `not_started` | `in_progress` | `blocked` | `done`

## Current focus

| Field | Value |
| --- | --- |
| Slice | 2 — Achievements |
| Branch | `feature/achievements` |
| Next gate | Gate 2 — user review of Succès flows (submit / approve / evidence) |
| Blocker | None. Local still uses `USE_SQLITE=true` without Postgres. |
| Notes | Gate 1 validated. Achievements implemented; automated AC-02/03/11 green. Awaiting user confirmation. |

## Slice status

| Slice | Name | Status | Branch | Gate validated | Started | Finished |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Foundation and permissions | `done` | `feature/foundation` | Yes (user 2026-09-28) | 2026-09-28 | 2026-09-28 |
| 2 | Achievements | `in_progress` | `feature/achievements` | No | 2026-09-28 | — |
| 3a | Monthly planning | `not_started` | `feature/planning` | No | — | — |
| 3b | Attendance and contractual comparison | `not_started` | `feature/attendance` | No | — | — |
| 4 | Leave | `not_started` | `feature/leave` | No | — | — |
| 5 | Shared reports and PWA | `not_started` | `feature/reports-pwa` | No | — | — |
| 6 | Self-hosted release | `not_started` | `feature/self-host` | No | — | — |

## Active gate checklist (slice 2)

- [x] Categories Video / Avis client seeded (`seed_achievement_categories`)
- [x] Submit with URL and/or image; private evidence route
- [x] Employee pending; manager on-behalf → Approved; manager self → Pending
- [x] Approve / reject / void / correct with revision + audit
- [x] Counts by occurrence date; pending/rejected listed separately in UI
- [x] AC-02 / AC-03 / AC-11 automated tests (+ employee cannot approve)
- [x] Reject unsafe URL / bad uploads; unauthorised evidence denied (404)
- [ ] User confirms before slice 3a

## History

### 2026-09-28 — Achievements slice implemented

- App `achievements`: categories, Achievement/Evidence, private `/evidence/<id>/`, workflow services, French UI list/create/detail.
- Audit: `MutationReceipt` + `record_audit` on submit/decide/void/correct.
- Tests: `DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test achievements.tests accounts.tests` → **11 OK**.
- Commands: `seed_achievement_categories`; local migrate with `USE_SQLITE=true`.
- Next: user tries Déclarer un succès / approbation gérant; then gate → planning (3a).

### 2026-09-28 — Gate 1 validated; start achievements

- User confirmed foundation works. Slice 1 marked `done`.

### 2026-09-28 — Foundation scaffold on `feature/foundation`

- `.venv`, Django 5.2.17, accounts/audit, French shell, Tailwind/daisyUI, access tests.

### 2026-09-28 — Local setup: mandate `.venv` / Progress tracking adopted
