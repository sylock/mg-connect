# Monthly planning and shared agenda

Version 0.3 · 28 September 2026. User scope additions are confirmed inputs; detailed publication and comment-visibility semantics below are explicit design proposals.

## Four separate concepts

| Concept | Purpose | Changes actual attendance? |
| --- | --- | --- |
| Contractual schedule | Effective-dated contract baseline and weekly/daily expected duration. | No |
| Usual weekly pattern | Start/end times and planned breaks used to initialise future monthly drafts. May initially match the contract, but is a separate record. | No |
| Monthly plan | Manager-prepared employee/date events, with Draft/Published lifecycle. | No |
| Clock records | What actually happened, with audited corrections. | Yes, through attendance correction only |

A manager can declare an employee before issuing a login. Use Employee as the employment identity; User optionally links to one Employee. Publishing a month includes every employee whose employment overlaps it. Missing usual patterns must be flagged, not interpreted as a day off. Explicit Rest events distinguish deliberate zero planned time from missing planning.

## Preparation

Initialise a month from each employee's effective usual pattern, holiday selections and existing approved leave. A weekly pattern has local work intervals and planned unpaid break minutes; validate intervals and daily duration. One-click generation is idempotent and never overwrites manual edits or comments. Regeneration offers a preview of affected dates and requires a deliberate selection before replacing draft content.

Managers may add/change work intervals, Rest, known leave, Holiday and Other events and comments. An Other event has a label and optional local interval; its default time effect is Information only. A proposed selectable Planned work effect allows training or meetings to contribute planned work once. Overlapping counted intervals are invalid; information-only events may overlap work. No hidden inference of paid time from an event label.

Known leave created by a manager during preparation is provisional until publication. Store a linked manager-entered leave record with state Draft and source ManagerPlanning, with a reason and proposed treatment. It becomes Approved atomically with publication. It is not an employee request awaiting approval. Existing approved leave is reused, never copied into a second absence. Draft known leave can be revised/removed without affecting live reports.

Employee-requested leave follows the independent request workflow. Approved requests are authoritative overlays, immediately visible to the whole team with private motives removed. If no month exists, the agenda can show approved leave with “Work schedule not published” for work dates. Rejected/pending requests do not block published work and are not displayed as accepted leave.

## Draft ↔ Published

Proposed first-version semantics:

1. A new month is Draft, visible only to managers. Employees see that the work schedule has not yet been published.
2. Publish validates employee/date coverage, intervals, missing data and absence conflicts. It creates an immutable numbered snapshot and activates draft manager-entered leave. The latest snapshot becomes visible to every active user.
3. Reopen changes the editing state to Draft and clones the latest published snapshot as a working revision. The previous published version remains visible, labelled with its publication date/version. Do not silently withdraw the only schedule employees already rely on.
4. Publish again replaces the public work plan with a new snapshot, retaining prior snapshots and who changed what. Failed validation leaves the earlier version untouched. Reopening without changes never alters published values.
5. “Unpublish and hide the previous version” is not part of this proposed default. If the owner wants that behaviour, clarify and revise the rule explicitly; do not silently equate reopening with erasing history.

Approved leave after publication updates the public agenda through an overlay without publishing unrelated draft edits. The current effective agenda is the published work snapshot plus current approved leave and applied calendar information from that snapshot. Flag affected working drafts as needing reconciliation. Publication must re-read current leave and reject a stale revision if its conflict review is no longer valid.

An approved full-day leave event masks that date's planned work, but retains the underlying work intervals so cancellation restores the baseline. If cancellation restores a work/holiday conflict, require manager review and mark the comparison provisional. A manager wanting work on a day with approved full-day leave must explicitly cancel/change the leave; editing a shift cannot silently revoke the decision.

All leave application and reversal is idempotent. Multi-month employee requests update each relevant agenda overlay in one transaction; they do not publish any month. Manager-entered known leave is split into per-month records for publication, linked by a common batch ID if entered together. Publishing one month must not approve unpublished leave in another.

## Holidays for Brussels-Capital

Location defaults: country BE, region Brussels-Capital, timezone Europe/Brussels, private-sector context. Each year propose the ten Belgian statutory holiday dates: New Year, Easter Monday, Labour Day, Ascension, Whit Monday, National Day, Assumption, All Saints, Armistice and Christmas. Generate movable dates locally with tested date logic or a maintained open-source holiday library; no paid API is needed.

Display proposal name/date/source separately from its application to the salon/employees. Managers can select which dates to apply, specify affected employees and calculation treatment, add extra closure dates and assign replacement dates with a link to the original holiday. Selections initially populate drafts; changing the holiday settings later does not silently rewrite a published work snapshot. Reopen/review/publish affected months to apply changes.

A replacement transfers the selected holiday effect to the replacement date for the affected employees; do not neutralise both dates for the same entitlement. Keep the original holiday label as reference if useful. Repeated generation must not duplicate holiday events. A full-day applied holiday masks planned work under the proposed default; intentionally working that date requires an explicit manager exception and treatment review before publication.

The statutory catalogue is not a list of optional employment rights. Selection controls the application's calendar and modelling; it does not decide whether work on that date or a replacement arrangement is legally valid. Do not automatically apply regional public-administration holidays to a private salon. Sector-specific and individual treatment is not inferred by this MVP.

Official reference consulted 28 September 2026: [SPF Emploi — Jours fériés](https://emploi.belgique.be/fr/themes/jours-feries-et-conges/jours-feries), sections listing ten holidays and explaining replacement days. This is the source for the proposed date catalogue, not a completed legal assessment of the salon.

## Comments and events

Managers can add/edit comments on any employee/date and on any Work, Leave, Holiday, Rest or Other event. An employee/date note does not require a work event. Comments preserve author, creation/edit timestamps and audit history; support plain text with safe escaping, not executable HTML.

Proposed visibility choices: Team comment (visible to all after publication) or Manager reminder (visible to managers only, default for new notes). Leave request reasons remain visible to the employee concerned and managers; do not automatically copy them into team comments or event titles. Use neutral labels such as “Congé”. Employee comment authoring is not required in this first version.

Team comments in a draft become public only with publication. A later public comment edit follows the same draft/publication flow. Private manager reminders can be updated immediately and are not exposed in published snapshot payloads. Employee/date and source-event links remain stable across revisions, so notes survive leave masking, regeneration and cancellation. A note on a retired event remains in manager history and can be explicitly reassigned; never silently discard it.

## Three views and two distinct differences

| View | Contents |
| --- | --- |
| Shared agenda | Published work intervals, breaks, leave, holidays, rest and other events for all employees; team comments. Manager can switch to clearly labelled draft preview. |
| Actual attendance report | Original/effective clock intervals, actual breaks, worked totals, correction flags and incomplete entries; independent of publication. |
| Combined report | Published planned intervals/events alongside actual intervals; planned versus actual duration, plus a separate contractual comparison. |

All three accept the existing month/year/range/distinct-date selectors and team/employee filters. A phone can use an employee/date list rather than a wide desktop grid. Approval overlays have decision timestamps; display published version plus “updated by approved leave” where relevant. Managers can inspect prior immutable publications; default employee reports use the latest effective published version, never draft values.

Define for each elapsed date:

- C = contractual baseline minutes; E = adjusted contractual expectation from BUSINESS_RULES.md.
- Q = published planned counted work before approved leave/full-day holiday masking, net of planned unpaid breaks.
- P = effective published planned work after masking; full-day leave or non-working holiday yields zero. Do not subtract leave again from P.
- W = actual closed elapsed seconds minus actual unpaid breaks.
- Planning difference = W − P × 60.
- Contractual difference = W − E × 60.
- Optional diagnostic planning allocation difference = P − E, displayed in minutes if useful.

Planned breaks and actual breaks are separate inputs. Unplanned actual work remains visible. A published Rest day is P=0; a missing/unpublished work plan is P=unknown, never zero. Contractual comparison may still be available when planning is missing, and attendance is always available. Conversely a plan must not fabricate a missing contract baseline. Apply each completeness status independently.

Example: adjusted contractual expectation 8 h, published work 7 h, actual 7 h 30 → planning difference +30 min; contractual difference −30 min. Do not label both as the same “overtime”. Whole-year completed totals exclude today/future dates as before. Schedule republishing changes the current comparison, so display its version; prior published snapshots remain inspectable without altering actual records.

## Visual implementation

Apply [UI_GUIDELINES.md](UI_GUIDELINES.md) for event colours, desktop/mobile views, manager editing controls and publication labels. Visual changes do not alter the planning and leave rules above.
