# MVP requirements

Status: specified draft v0.3 · 28 September 2026

U = directly requested by the user. P = proposed implementation or business default. All rows are allocated to MVP unless explicitly deferred. U indicates provenance, not formal approval of every detail. Detailed operational policies are in BUSINESS_RULES.md.

## Business needs and capabilities

| ID | Need |
| --- | --- |
| BN-001 | Recognise and count employee achievements with reliable evidence. |
| BN-002 | Share attendance and understandable contractual hour differences. |
| BN-003 | Request and decide leave in one simple application. |
| BN-005 | Prepare, publish and share monthly team schedules and compare planned work with actual attendance. |
| BN-004 | Own an open-source, self-hostable tool without mandatory software subscriptions. |

| ID | Capability | Needs |
| --- | --- | --- |
| CAP-001 | Accounts and roles | BN-001, BN-002, BN-003, BN-004 |
| CAP-002 | Achievements | BN-001 |
| CAP-003 | Attendance and schedules | BN-002 |
| CAP-004 | Leave | BN-003, BN-002 |
| CAP-005 | Shared reports | BN-001, BN-002, BN-003 |
| CAP-006 | Mobile web and operations | BN-004 |
| CAP-007 | Monthly planning and shared agenda | BN-002, BN-003, BN-005 |

## Actors and access

Proposed two business roles: Employee and Manager. Every active account has Employee capabilities; Manager adds administration and approval. Multiple managers are supported. A technical superuser exists for recovery only and is not an extra everyday role. Self-approval rules are provisional in BUSINESS_RULES.md.

| Action | Employee | Manager |
| --- | --- | --- |
| View and generate team reports | Yes | Yes |
| Submit own achievement and evidence | Yes | Yes |
| Record achievement for another employee | No | Yes |
| Decide submitted achievements | No | Yes, subject to self-approval rule |
| Clock own arrival/departure | Yes | Yes |
| Correct time records | No | Yes, with reason and history |
| Submit own leave request and reason | Yes | Yes |
| Accept/refuse leave | No | Yes, subject to self-approval rule |
| View another employee's leave reason | No (proposed privacy default) | Yes |
| Manage employees and usual schedules | No | Yes |
| Manage accounts, manager membership and contractual schedules | No | Yes (proposed access details) |
| View published team agenda | Yes | Yes |
| Prepare monthly drafts, publish or reopen them | No | Yes |
| Enter known leave and event/day comments | No (proposed authoring limit) | Yes |

Anonymous visitors cannot access operational data. “Everyone” means all authenticated active salon accounts, not the public internet.

## Functional requirements

| ID | Requirement | Basis | Acceptance reference |
| --- | --- | --- | --- |
| REQ-CAP001-001 | Support individual authenticated accounts and a Manager role assignable to multiple users. | U | AC-01 |
| REQ-CAP001-002 | Allow managers to create/deactivate accounts and assign/revoke manager membership; retain historical records and prevent removal of the last active manager. | P | AC-01 |
| REQ-CAP002-001 | Record an achievement for an employee, its category, occurrence date and proof consisting of a URL, image or both. Initially provide Video published and Positive customer review. | U | AC-02 |
| REQ-CAP002-002 | Allow employees to submit their achievements for manager approval or refusal. | U | AC-02 |
| REQ-CAP002-003 | Allow a manager to record achievements on behalf of an employee, keeping the actual author distinct from the beneficiary. | U | AC-03 |
| REQ-CAP002-004 | Count only approved, non-voided achievements; show pending and rejected entries separately to the employee and managers. | P | AC-02, AC-03 |
| REQ-CAP002-005 | Allow a manager to correct or void an achievement with a reason and audit trail; retain proof history and prevent silent double counting. | P | AC-03 |
| REQ-CAP003-001 | Allow each user to clock arrival and departure through the website or installed PWA. | U | AC-04 |
| REQ-CAP003-002 | Store each employee's effective-dated contractual schedule, including daily expected minutes and weekly total. | P, needed for requested comparison | AC-05 |
| REQ-CAP003-003 | Allow managers to add missing attendance, correct times and enter unpaid break duration, with a mandatory correction reason. | U for corrections; P for break input | AC-06 |
| REQ-CAP003-004 | Preserve original clock events and all corrections; mark missing, invalid or overlapping records instead of fabricating attendance. | P | AC-04, AC-06 |
| REQ-CAP004-001 | Allow a user to request leave for one date, a date range or several distinct dates, with a mandatory reason. | U | AC-07 |
| REQ-CAP004-002 | Allow managers to accept or refuse a leave request and record the decision author/time. | U | AC-07 |
| REQ-CAP004-003 | Show the requester their request status and manager response. Require a response for refusal. | P | AC-07 |
| REQ-CAP004-004 | Support a manager's audited cancellation of approved leave and requester withdrawal of pending leave. | P | AC-08 |
| REQ-CAP005-001 | Allow every business role to generate and view an on-screen report for a month, year, inclusive custom date range or selection of distinct dates. | U | AC-09 |
| REQ-CAP005-002 | Allow every authenticated user to view the report for the whole team or an individual employee. | U | AC-01, AC-09 |
| REQ-CAP005-003 | Display approved achievement counts by category and employee in the selected period. | U | AC-02, AC-09 |
| REQ-CAP005-004 | Display worked duration, contractual duration, approved absence adjustment, adjusted contractual expectation and positive/negative contractual difference by employee/date, with period totals; keep this distinct from the planned-work comparison. | U for comparison; P for breakdown | AC-05, AC-09, AC-18 |
| REQ-CAP005-005 | Reflect manager corrections in regenerated reports and expose the presence of corrections. | U | AC-06 |
| REQ-CAP005-006 | Identify provisional/incomplete calculations, missing schedules, missing clocks and unconfigured absence/calendar rules without presenting them as a definitive balance. | P | AC-10 |
| REQ-CAP005-007 | Share report figures and leave dates/status with the team; restrict free-text leave reasons, private correction explanations and evidence files to the concerned employee and managers. | P | AC-01, AC-11 |
| REQ-CAP006-001 | Deliver a responsive web application installable on supported Android and iOS browsers as a PWA. | U | AC-12 |
| REQ-CAP006-002 | Deliver source code under an open-source licence and documented self-hosting, without a mandatory paid service. | U | AC-13 |

## Monthly planning additions

| ID | Requirement | Basis | Acceptance reference |
| --- | --- | --- | --- |
| REQ-CAP001-003 | Allow managers to declare employees and maintain their employment dates and usual working pattern, independently of account activation. | U; P for account separation | AC-14 |
| REQ-CAP007-001 | Store an effective-dated usual weekly pattern with working start/end times and planned breaks per employee. | U; P for versioning | AC-14 |
| REQ-CAP007-002 | Allow managers to initialise and edit a monthly schedule for all employees from their usual patterns. | U | AC-14 |
| REQ-CAP007-003 | Allow managers to add already-known employee leave while preparing the monthly schedule. | U | AC-15 |
| REQ-CAP007-004 | Support Draft and Published states with manager transitions in both directions and publication history. | U; P for history | AC-16 |
| REQ-CAP007-005 | Allow all authenticated users to view the published schedule of all employees; restrict unpublished work to managers. | U; P for draft visibility | AC-16 |
| REQ-CAP007-006 | Propose year-specific holidays for the Brussels-Capital location and let managers choose their application, add other dates and specify replacement days. | U; P for replacement details | AC-17 |
| REQ-CAP007-007 | Display approved employee leave automatically in the shared agenda, keeping it linked to its request/decision and preventing duplicate manual leave. | U | AC-15 |
| REQ-CAP007-008 | Support work, leave, holiday, rest and other agenda events for each employee/date. | U for work/leave/other; P for categories | AC-19 |
| REQ-CAP007-009 | Allow managers to attach comments to any event or to an employee/date, including days without a work event. | U; P for authoring permission | AC-19 |
| REQ-CAP007-010 | Distinguish published team-visible event comments from private manager reminders; record comment changes. | P | AC-19 |
| REQ-CAP005-008 | Provide a separate actual-attendance report independent of monthly planning publication. | U | AC-18 |
| REQ-CAP005-009 | Provide a combined report showing published planned work, actual work and the signed difference, with event/date details and the contractual comparison retained separately. | U | AC-18 |

## Quality and operational requirements

| ID | Requirement | Basis | Acceptance reference |
| --- | --- | --- | --- |
| REQ-CAP006-003 | Authorise all server operations, use secure authentication/CSRF controls and validate proof uploads. | P | AC-01, AC-11 |
| REQ-CAP006-004 | Persist data and evidence across restarts; provide backup and restore instructions. | P | AC-13 |
| REQ-CAP006-005 | Require online acknowledgement for mutations; make retries safe and never display success before persistence. | P | AC-04, AC-12 |
| REQ-CAP006-006 | Provide French mobile-first screens with labelled controls, keyboard access, readable contrast and status text not conveyed by colour alone. | P | AC-12, AC-20 |
| REQ-CAP006-007 | Provide a polished, colourful and responsive interface using the shared visual guidelines across employee and manager screens. | U | AC-20 |
| REQ-CAP006-008 | Use Django templates, Tailwind CSS, daisyUI and HTMX for the selected frontend approach, with locally built/served assets and no required paid UI component service. | U for selected stack; P for delivery details | AC-20, AC-21 |

## Deliberately deferred

Payroll, legal overtime premiums, leave entitlement balances/accrual, automatic social-media/review collection, reward purchases, rankings, GPS/biometrics, automatic shift optimisation, partial-day leave, multi-salon tenancy, offline writes, push/email notifications and CSV/PDF exports. The app reports an operational time difference, not payroll-approved overtime. Browser printing is not a dedicated export feature.

## Proposed screens

Shared team agenda; Manager monthly planning editor with Draft/Published state; Holiday selection; Employee usual-pattern editor; Home with today's clock status and actions; My achievements; New achievement; My leave; New leave request; Actual attendance report; Planned-versus-actual report; Achievement report; Manager approvals; Attendance corrections; Accounts and contractual schedules. Keep these as simple pages; no separate dashboard builder.
