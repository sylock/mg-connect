# Implementation plan

All user-requested capabilities belong to the first usable release. The slices below are a delivery order, not removal of scope. Confirm provisional business choices as real data becomes available.

Track live status, gates and session history in [PROGRESS.md](PROGRESS.md). Do not overwrite this plan with transient status; update PROGRESS instead.

## 1. Foundation and permissions

Create Django project, supported Python environment **via a project `.venv`**, locked dependencies installed into that venv (never system Python), PostgreSQL setup, custom user model before initial migrations, Employee/Manager permissions, French responsive shell using UI_GUIDELINES.md, Tailwind CSS + daisyUI theme, locked CSS build, locally served HTMX, login/logout and manager account workflows. Add MIT licensing information and dependency notices. Test access denial and team-report permission before feature work.

Deliver runnable documented local setup, synthetic fixtures and migration checks. Do not seed actual names or work schedules from assumptions. Holiday catalogues provide suggestions only until managers select their application.

Before feature expansion, render the shared components and a synthetic home/agenda screen at phone and desktop widths to verify the visual direction. Keep all product UI distinct from Django admin.

## 2. Achievements

Implement categories, submission with URL/image, private evidence serving, manager review, on-behalf entry, correction/void and audit. Add simple on-screen counts and date filtering using the shared report date selector. Verify AC-02/03/11 and permissions.

## 3a. Monthly planning

Implement Employee master data independently of optional login, effective usual patterns, month generation, event editing and comments. Add Brussels/Belgium holiday proposals with selectable application/replacements. Add Draft/Published transitions and immutable publications, retaining the previous public version during draft editing. Integrate manager-entered draft leave activation on publication and explicit Rest coverage. Verify AC-14/16/17/19 with permission and concurrency checks.

## 3b. Attendance and contractual comparison

Implement server-time arrival/departure, effective-dated schedules, date overrides, daily break input, manager corrections and audit. Build the pure calculation/query service and incomplete/provisional reporting. Verify concurrency, DST, missing records and schedule changes on PostgreSQL.

## 4. Leave

Implement full-day multi-date requests, mandatory reason, manager acceptance/refusal, treatment configuration, withdrawal/cancellation and overlap prevention. Integrate approved adjustments into the existing calculation service and linked public agenda overlays, without publishing unrelated drafts. Verify AC-07/08/15 and calculation edge cases.

## 5. Shared report and PWA

Complete shared agenda, actual attendance and combined team/individual views with month, year, range and distinct-date modes. Include event comments according to visibility, achievement categories, planned work, baseline/adjusted contractual expectation, actual work, leave and both distinct differences. Verify AC-18; never substitute draft work for published work. Exclude private free text from team view. Add manifest, icons, installation help and restricted static-only offline fallback. Test employee and manager flows on desktop and mobile. Verify AC-20/21, private HTMX history handling, keyboard focus after partial updates and production CSS generation.

## 6. Self-hosted release

Create production configuration, example environment, container/Compose definitions, persistent volumes, HTTPS instructions, database migration/runbook, backup and restore instructions. Document how to bootstrap the first manager and reset access. Run security/deployment checks and demonstrate restore. Provide a complete requirement-to-test result summary; do not mark untested behaviour complete.

## Suggested first prompt for an implementation AI

> Read AGENTS.md and all linked project specifications, especially PLANNING.md and UI_GUIDELINES.md. Summarise confirmed scope and proposed defaults briefly, then implement slice 1 and proceed through the plan in reviewable increments. Use synthetic data until actual schedules and policies are supplied. Keep all requested MVP features in scope. Do not invent contractual, break or leave rules. Maintain traceability to requirement IDs and report test evidence honestly. Deliver a self-hostable application with no mandatory paid service. Do not publish or deploy externally without an explicit instruction in the active task.

## Completion checklist

- Every U requirement demonstrably works; proposals are documented and visible.
- All employees can view the published team agenda and reports; only managers edit/publish plans and correct/approve.
- Approved leave overlays, comments and holiday replacements preserve publication boundaries and avoid duplicate adjustment.
- Repeated and concurrent submissions cannot double-count work or achievements.
- Reports show trustworthy calculation status and preserve historical evidence.
- PWA works through HTTPS; unavailable network never creates false clock confirmation.
- Source, migrations, setup, configuration examples, licence and restore procedure are included.
- Tailwind/daisyUI assets build reproducibly; HTMX flows and the rendered visual design are verified on mobile and desktop.
- Remaining decisions and verification limits are explicit; no hidden paid dependency.
