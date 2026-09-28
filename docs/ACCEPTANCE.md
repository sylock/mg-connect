# Acceptance scenarios

Use synthetic employees and two managers. Associate automated tests with the requirement IDs from REQUIREMENTS.md. The dates below are fixtures, not actual salon schedules.

| ID | Scenario | Expected result |
| --- | --- | --- |
| AC-01 | Employee opens another employee's team report, then attempts to approve leave, alter a schedule or fetch their private proof directly. | Team figures visible; prohibited writes and private evidence denied server-side. Anonymous report access denied. Both managers can review requests; last-manager removal blocked. |
| AC-02 | Submit a video dated 10 September with a screenshot; approve it on 2 October. | Pending counts zero; approval adds one to September, not October. October regeneration shows no September occurrence. Rejection remains zero. |
| AC-03 | Manager records an achievement for employee B; retries identical request; later voids it with a reason. | One approved occurrence under proposed rule; manager remains author, B beneficiary; after void count zero and original/audit history retained. Manager self-submission remains pending. |
| AC-04 | Double-tap arrival, retry after a timeout, then clock departure; try a second overlapping interval. | One open interval only; retry returns original outcome; departure closes it once; invalid/overlapping operation rejected. No clock-in uses editable client time. |
| AC-05 | Configure 38 h expected over an elapsed week; one approved neutralising leave day of 7 h 36; closed worked total 31 h 24. | Baseline 38 h, leave adjustment 7 h 36, adjusted expectation 30 h 24, worked 31 h 24, difference +1 h. |
| AC-06 | Correct a closed interval from 09:00–17:00 to 09:00–17:30, no break; retry stale correction. | Worked total rises by 30 minutes; manager/reason/before/after retained; stale correction conflicts rather than overwriting. |
| AC-07 | Employee selects 3, 5 and 8 October, supplies a reason; manager approves or rejects the complete request. | Exactly three dates, not the intervening days. Approval records actor/treatment; rejection requires response and gives zero leave adjustment. Two simultaneous conflicting approvals cannot both succeed. |
| AC-08 | Cancel an approved neutralising leave day with a reason. | Expected time is restored in live reports; previous approval and cancellation remain auditable; no hard deletion. |
| AC-09 | Generate month, year, date range and distinct-date views as employee and manager. | Same team totals for same dates; inclusive boundaries; dates deduplicated; no unselected dates; agenda, actual attendance and combined views all offer the filters. |
| AC-10 | Request a year including future dates, one missing schedule day and one forgotten departure. | Future projection separated; today/future do not create a final deficit; incomplete elapsed dates listed; no definitive period balance. Unconfirmed break/calendar policies explicitly mark provisional results. |
| AC-11 | Upload an oversized image, disguised HTML or SVG, or a javascript: proof URL; attempt direct unauthorised media access. | Rejected or denied; private files not served from public static paths; no backend fetching of submitted URLs; team report excludes private reasons/proofs. |
| AC-12 | Open on a narrow phone, install on supported Android/iOS, disconnect network and attempt clock-in. | Usable French UI and installed launch; clear unconfirmed/offline state; no fake success or queued attendance; retry after reconnection is idempotent. |
| AC-13 | Fresh self-hosted setup from documentation; restart services; back up then restore to a separate environment. | Accounts, time events, history and proof images survive; no paid service required; licence/dependency inventory included. |

## Planning acceptance scenarios

| ID | Scenario | Expected result |
| --- | --- | --- |
| AC-14 | Declare employee without login; set usual Monday 09:00–17:30, planned unpaid break 30 min; initialise month twice, then change future usual pattern. | Employee appears in planning; net 8 h on relevant Mondays; no duplicates; manually edited dates and prior publications unchanged. Contract baseline remains separate. |
| AC-15 | Enter known leave in a draft; publish; subsequently approve employee leave while unrelated draft shifts are being edited; cancel the approved leave. | Draft known leave not public before publication; afterwards a single linked approved absence. Later accepted leave appears immediately, without draft shifts leaking. Cancellation restores underlying work. Multi-month leave is idempotent and atomic. |
| AC-16 | Publish version 1, reopen and edit to a shorter day, inspect as employee, then republish. | Editing state Draft; employee still sees v1. Republish shows v2; v1 preserved. Failed/stale publication changes nothing public; actual clock records unchanged. |
| AC-17 | Generate holiday proposals for two years, apply a subset and a replacement date; regenerate; modify selections while a month is published. | Correct yearly fixed/movable dates; choices/replacement linkage retained; no duplicates or automatic regional public-service additions; existing publication unchanged until republish; no double credit. |
| AC-18 | Contractual expectation 8 h; published net work 7 h; actual 7 h 30. Repeat with unpublished plan, then explicit published Rest. | Combined differences +30 min vs plan and −30 min vs contract. Unpublished plan: planning difference unknown, actuals remain visible. Rest: P=0 and actual work is unplanned. |
| AC-19 | Add team comment to Work and Leave, private reminder to Other, and a day note on a Rest date; reopen/regenerate/cancel leave. | All event types support comments; only published team text visible to employees; manager-only reminders never in response payload; private leave reason not copied to shared text; history/links preserved. |

## Calculation edge cases

These fixtures assume closed elapsed dates and confirmed policies unless stated otherwise.

| Case | Inputs | Expected |
| --- | --- | --- |
| Negative difference | Expected 8 h; worked 7 h 30; no leave | −30 min. |
| Break | 09:00–17:30 closed interval; unpaid break 30 min; expected 8 h | Worked 8 h; difference 0. |
| Clocked-out break | 09:00–12:00 and 12:30–17:30; unpaid break 0 | Worked 8 h; no second deduction. |
| Schedule change | One selected Monday before change expects 8 h; next Monday expects 6 h | Total baseline 14 h, not 12 h or 16 h. |
| Holiday override | Schedule 8 h; explicit local-date override 0; no work | Baseline and difference 0 for that day. |
| Leave on non-working day | Schedule 0; approved neutralising leave | Leave adjustment 0. |
| Pending leave | Expected 8 h; no work; leave still Pending | Adjustment 0; elapsed-day difference −8 h, with pending leave visible. |
| Work during leave | Expected 8 h; neutralising leave 8 h; worked 2 h | Arithmetic +2 h, but provisional conflict until resolved. |
| Overnight | 28 Sep 23:00 to 29 Sep 01:00 local; report selects 29 Sep only | Exactly 1 h of work on selected date. |
| DST spring | Europe/Brussels 29 Mar 2026 01:30 to 03:30 local | Actual elapsed work 1 h. |
| DST autumn | Europe/Brussels 25 Oct 2026 01:30 to 03:30 local | Actual elapsed work 3 h. |
| Ambiguous correction time | Manager enters 25 Oct 2026 02:30 local | Require explicit offset/first-or-second occurrence; do not guess. Reject nonexistent spring time. |
| Rounding | Two intervals of 30 seconds each | Sum first: display 1 minute, not 2. |
| No selected elapsed dates | Only today/future selected | Show ongoing/projection; completed difference N/A, not a deficit. |

## Release evidence

Record commands executed and actual results in the implementation PR or delivery note. Include screenshots of mobile report, approval and correction screens using synthetic data. A specification scenario is not evidence that a test has passed. Automated browser emulation does not prove real iPhone installation.

## Planning-specific checks

- Leave and holiday on the same date neutralise contractual expectation at most once; effective plan already masked to zero is not reduced again.
- Approved leave during simultaneous publication is either included in its validation or rejected as a stale publication; no partially published request or deadlock.
- Daily planned intervals and planned breaks differ from actual clock intervals/breaks without rewriting either source.
- Missing usual pattern cannot silently generate Rest. Every employee/date in a published month is explicitly covered or publication fails with an actionable list.
- A manager private reminder created during draft editing cannot leak via public snapshot JSON, HTML attributes, event search or report views.
- Validate Easter Monday, Ascension and Whit Monday for at least two known years against the official holiday definitions; fixed dates retain their calendar day even when not operationally selected.

## UI acceptance additions (v0.3)

| ID | Scenario | Expected result |
| --- | --- | --- |
| AC-20 | Inspect the six key screens specified in UI_GUIDELINES.md at 360, 768 and 1440 px, with long French labels and keyboard navigation. | Consistent ivory/plum/coral theme; readable labelled event colours; desktop planning grid and usable mobile daily list; no whole-page overflow; focus/contrast/touch targets checked; draft and published views unmistakable. |
| AC-21 | Change report filters and approve a request via HTMX; trigger validation error, expired session, stale revision and a network timeout. | Correct authorised fragments; CSRF enforced; useful errors and preserved inputs; no duplicate mutation or premature success; full login redirect; no authenticated HTML in HTMX localStorage history. |

These add to AC-01 through AC-19; they do not replace planning, permission, calculation or PWA installation tests. Inspect the production CSS build too, so missing dynamically generated classes are caught.
