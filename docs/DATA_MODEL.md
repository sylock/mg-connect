# Initial logical data model

Package version 0.3. The frontend update does not alter the planning or attendance model.

This is a proposed implementation model. UUID primary keys are suggested for externally addressed records. Foreign keys to employees must preserve history when accounts are deactivated. Store UTC timestamps and explicit local dates where business dates matter.

| Entity | Essential fields | Invariants |
| --- | --- | --- |
| User | Django user fields, display_name, active, optional employee link | Manager group adds privileges; no public signup; deactivation does not cascade-delete records. |
| Employee | display_name, active, employment_start, employment_end | Employment identity can exist before a login; domain employee foreign keys reference this entity. |
| ScheduleVersion | employee, effective_from, effective_until exclusive, weekly_minutes, weekday_minutes for seven days, revision | Versions cannot overlap; seven daily values sum to weekly total; validate actual employment span. |
| DateOverride | employee, local_date, expected_minutes, reason, author, revision | One effective override per employee/date, audited history. |
| CalculationSettings | timezone, break_policy_confirmed, calendar_year confirmations, leave_treatment definitions | Explicit settings; no real contracts or holidays seeded automatically. |
| AchievementCategory | code, label, active | Seed the two requested codes; retain disabled category history. |
| Achievement | employee, created_by, category, occurred_on, state, reviewed_by, reviewed_at, review_note, revision | Pending/Approved/Rejected/Voided; counts only Approved; retain actual actor and beneficiary. |
| Evidence | achievement, kind, safe_url or storage_key, mime_type, size, original_label, created_by, superseded_at | URL or image; approved record evidence is not silently overwritten. |
| ClockEvent | employee, kind, received_at, actor, idempotency_token | Immutable original live event, server timestamp; unique actor/token. |
| WorkInterval | employee, effective_start, effective_end nullable, original_in_event, original_out_event, state, revision | End after start; no effective overlap; max one open interval; corrected/inserted intervals retain history. |
| DayBreak | employee, local_date, unpaid_minutes, set_by, reason, revision | Unique employee/date; cannot exceed closed elapsed work; zero explicitly allowed. |
| LeaveRequest | employee, submitted_by, source, reason, state, decision_by, decision_at, decision_note, treatment, revision, planning_month, batch_id | EmployeeRequest uses Pending workflow; ManagerPlanning may start Draft, approved on its month publication; immutable decision history. |
| LeaveDate | request, local_date | Unique request/date; no competing Pending/Approved requests per employee/date. |
| AuditEvent | actor, entity_type, entity_id, operation, before, after, reason, timestamp, correlation_id | Append-only through ordinary app permissions; restrict sensitive before/after values to authorised viewers. |
| MutationReceipt | actor, action, token, request_hash, result_reference, created_at | Unique actor/action/token; same token with a different payload is rejected. |

## Concurrency design

Lock the Employee row while opening/closing/correcting attendance or approving/submitting leave, so competing actions for the same employee serialize. Use a PostgreSQL partial unique constraint for one open, non-void interval. Enforce interval overlap protection with an exclusion constraint where practical, plus transactional validation. Revalidate unpaid breaks after any correction.

Leave dates span multiple requests: cross-request overlap cannot be enforced by uniqueness on request/date alone. Lock employee, query competing Pending/Approved dates and enforce rejection transactionally. All writers, including admin workflows, must use the same service. Add PostgreSQL concurrency tests.

Approval/correction uses an expected revision and a conditional state transition. Persist audit changes in the same transaction. Use idempotency receipts for user mutations; do not regard a disabled button as sufficient duplicate prevention.

## Derived data

Do not persist editable achievement counters or monthly hour balances as the source of truth. Derive reports from effective intervals, contractual schedule versions, date overrides, effective holiday selections, approved leave treatment, published planning snapshots and approved achievements. A report result includes selected dates, completed cutoff, generated_at, per-day values, completeness status and anomalies.

Do not model approved leave as worked attendance. Do not use an editable net-difference field to fix missing clocks. Corrections alter the underlying records with history and trigger recalculation.

## History boundaries

Audit history is protected against normal user/manager edits, not cryptographically tamper-proof against the server/database administrator. Backups preserve original events, effective records and evidence together. Never claim a stronger guarantee than implemented.

## Planning model additions

| Entity | Essential fields | Invariants |
| --- | --- | --- |
| UsualPatternVersion | employee, effective dates, weekday work intervals, planned break minutes, revision | No overlapping versions; separate from contractual ScheduleVersion. |
| MonthlyPlan | year, month, edit_state, draft_revision, last_published_snapshot, updated_by | One per salon/month; Draft may coexist with a previous public snapshot. |
| PlanDay | monthly_plan, employee, local_date, coverage_status | One per employee/date; explicit Rest vs incomplete/missing; includes employees active during month. |
| AgendaEvent | stable_id, plan_day, type, local start/end or all_day, planned_break_minutes, time_effect, source_leave, source_holiday, revision | Counted work intervals cannot overlap; source links prevent duplicate leave; Other is informational unless explicitly counted. |
| PublicationSnapshot | plan, version, published_at, published_by, immutable event/day/holiday data | Unique plan/version; frozen base work and public comments, no private notes in public payload. |
| HolidayProposal | year, country, region, code, proposed_date, label, source_version | Unique source/code/year; no operational effect by itself. |
| HolidaySelection | proposal or custom label, applied_date, affected employees, replacement_of, treatment, revision | Original/replacement entitlement linked; effects included in published snapshots and not duplicated. |
| EventComment | employee, local_date, optional stable_event_id, author, text, visibility, timestamps, revision | Team comments follow publication; manager reminders private; retain author/history. |

A snapshot carries the linked leave IDs and generation revisions, but approved leave is overlaid using its current authoritative state. Freeze original base intervals so cancellation can restore the planned baseline. The report identifies snapshot version and leave update timestamps. Do not mutate an immutable snapshot to implement an overlay.

Holiday effects become operational only with publication, unlike later approved employee leave which is immediately effective. Resolve contractual holiday adjustment from selected effective published application, capped with other neutralising absence. Replacement dates across months must reference both dates; show incomplete/provisional status until both affected months have consistent published selections, rather than double-crediting or silently dropping the entitlement.

Publishing validates draft manager-entered leave against existing Pending/Approved requests and known leave, using the same lock order as approval. Existing approved source records are reused. Removing an event is not permission to cancel its approved leave source. Draft revisions, public snapshots and attendance are independent histories.
