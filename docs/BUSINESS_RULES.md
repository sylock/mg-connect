# Business rules and calculations

Status: v0.3 proposed detailed defaults supporting user requirements. Read PLANNING.md for the new monthly planning lifecycle and its precedence over the former no-planning scope. Confirm operational settings before relying on live balances. These rules deliberately avoid inventing employment or payroll law.

## Achievements

- Initial categories: Video published; Positive customer review. One record means one occurrence, not an arbitrary points amount. No public leaderboard in MVP.
- Require beneficiary, occurrence date, category and at least one safe URL or image. Proposed cap: three JPEG/PNG/WebP files, 5 MiB each. Future achievement dates are rejected.
- An employee submission starts Pending. A manager may approve or reject it with an optional approval comment and mandatory refusal explanation.
- Proposed: a manager recording for another employee may save it directly as Approved. Record both `created_by` and `reviewed_by` even when they are the same person. Manager self-submissions remain Pending for another manager.
- Counts use occurrence date in the selected date set, not submission or approval date. Later approval therefore updates a historical report. Show the generation timestamp; reports are live, not frozen.
- Employees may edit only their pending entries. Approved records require a manager correction with a reason; retain old values and old evidence references. Void instead of delete.
- Repeated requests with the same idempotency token must create one record. Similar URL/employee/category submissions generate a duplicate warning, not a universal ban: the same evidence can sometimes concern multiple employees.

## Attendance

- Online self clocking uses server receipt time, not an editable phone clock. Save UTC instants; display Europe/Brussels local date/time.
- Proposed simple UI: Arrivée and Départ. Allow more than one closed interval a day, but at most one open interval per employee and no overlap. This supports leaving and returning without requiring a separate pause feature.
- Arrival when an interval is already open is refused. Departure without an open interval is refused. Repeated network requests are idempotent. Never automatically close a forgotten departure at midnight.
- A manager may insert a missing interval, adjust a boundary, set the day's unpaid break, or void a wrong interval. A reason and audit history are mandatory. Preserve original events; work from effective corrected intervals.
- Proposed break model: a daily unpaid break in minutes, entered/confirmed by a manager. No automatic deduction. If a break was already clocked out, do not deduct it again. Display break policy/configuration status. Zero is a deliberate configured choice, not an inferred contractual fact.
- Closed intervals crossing local midnight are divided at timezone-aware local day boundaries. Daily breaks attach to the selected local date and cannot exceed that date's total closed elapsed time. Duration is actual UTC elapsed seconds, including daylight-saving transitions.
- Current open intervals are visible as live elapsed time but excluded from completed totals. Missing historical departure prevents a definitive balance for that day and selected period.

## Contractual schedules and calendar

- Managers enter employment start/end dates and effective-dated weekly schedules: expected minutes for each weekday. Zero means a contractual non-working day; no schedule means unknown. Never assume a 38-hour week or that every employee shares the salon opening days.
- Daily minutes must sum to the declared weekly total. No overlapping schedule versions. A mid-month change splits calculation by effective date. Backdated edits require a reason, audit and a clear indication that historical live reports change.
- A date-specific contractual override may replace expected minutes for an employee, with a reason. Ordinary monthly planning changes must not alter it. Holiday dates are proposed automatically from the documented Belgian catalogue in PLANNING.md; application, treatments and replacement dates are manager-selected, not automatically inferred.
- Track confirmation of break policy and calendar coverage for the selected year. Unconfirmed coverage makes the balance provisional. Missing schedule data produces unknown expected duration, never zero.
- For dates wholly outside employment, expected duration is zero; erroneous time entries outside employment must be flagged for correction.

## Leave workflow

- The user selects one or more unique local dates (or a range expanded into dates), supplies a reason and submits. MVP is whole-day leave only.
- Request states: Pending → Approved or Rejected; Pending → Withdrawn; Approved → Cancelled by a manager with a reason. A rejected/withdrawn/cancelled request is terminal; create a new request to resubmit.
- Approval/refusal applies to the whole request in MVP. If only some days should be accepted, reject with an explanation and ask for separate requests. No hidden partial acceptance.
- Reject overlapping Pending/Approved leave dates for the same employee at submission and recheck at approval within a transaction. Concurrent approvals must not bypass this.
- Proposed: no manager self-approval of their own leave; another manager decides. Deactivation/role changes must not strand the last active manager.
- At approval a manager assigns an explicitly configured leave treatment. Accepted leave appears automatically as a linked agenda overlay (see PLANNING.md), even if no month has been published; it does not publish draft shifts. MVP treatments: Neutralise expected hours, or Keep expected hours. The labels are operational calculation choices, not legal/payroll categories. If no treatment is configured, no definitive balance is available; never guess from the free-text reason.
- Approved neutralising leave reduces contractual expected minutes by that date's contractual baseline, including an explicit contractual override. A contractual non-working day credits zero. Pending/rejected/withdrawn/cancelled leave contributes zero adjustment. Selected neutralising holidays use the same adjustment mechanism; union overlapping coverage and cap the total at the baseline, never subtract holiday and leave twice.
- Approved leave with recorded work on the same date is flagged for review, not silently removed or counted twice. Include the closed work, apply the configured adjustment, and label the resulting balance provisional until a manager resolves the conflict through a correction/cancellation.
- Motives are mandatory but do not solicit medical details. Proposed visibility: requester and managers only. Team reports show leave dates/status, not free text.

## Report period and formulas

All authenticated active employees and managers can generate team reports: agenda, actual attendance, combined planned-versus-actual and achievements. Actual attendance remains available without a published plan. Planning visibility and comparison rules are in PLANNING.md. Filters: month/year; whole calendar year; inclusive date range; non-contiguous selected dates. Sort and deduplicate the selected dates. A whole-year report includes future schedule projections but never treats future work as a deficit.

For an employee and each selected, elapsed local date d:

- `C(d)` = contractual minutes from the effective schedule or date override.
- `W(d)` = sum of valid, closed, effective interval seconds intersecting d, less recorded unpaid break minutes × 60.
- `L(d)` = union of approved neutralising leave and selected effective neutralising holiday coverage in minutes, capped at C(d); all other leave states contribute zero. Label this absence adjustment and show leave/holiday components separately without double counting.
- `E(d) = C(d) - L(d)` = adjusted contractual expected minutes (not monthly planned work).
- `D(d) = W(d) - E(d) × 60` = signed contractual operational difference in seconds. The separate planning difference is `W(d) - P(d) × 60`, where P comes from the effective published plan as defined in PLANNING.md.

Store/calculate with integer seconds; display durations as hours:minutes and label display precision. Aggregate exact seconds first, then round once to the nearest minute for display (30 seconds up in magnitude), so rounding is not applied per clock event. A negative difference retains its minus sign.

Period totals sum the selected elapsed dates only. Show baseline contractual time, worked time, leave adjustment, adjusted expectation and signed difference separately. Count achievements over all selected occurrence dates; they cannot be future-dated.

Today and future dates have a separate ongoing/projected section. Today's live work is informative; its final daily difference is excluded until the local day has elapsed, even if the employee has clocked out. Show the completed-date cutoff explicitly. This is a proposed simple rule, not an owner-approved settlement policy.

For missing contracts/clock-outs or unresolved overlaps, display the known subtotals, excluded dates and “Incomplete”; do not replace unknown inputs with zero. If all arithmetic inputs exist but break/calendar configuration is unconfirmed or work overlaps leave, display the numeric result as “Provisional” with reasons. A definitive complete-period difference is available only when every elapsed selected date is resolved and policy inputs are confirmed. No carry-over from dates outside the selected set.

Example: contractual 38 h, neutralising leave 7 h 36, worked 31 h 24 → adjusted expected 30 h 24 → difference +1 h. Do not add leave to both worked time and expected-time reduction.

## Choices still requiring owner input

| Topic | Proposed first-version choice | When input matters |
| --- | --- | --- |
| Visibility | All team figures visible to all active users; private reasons/proofs restricted. | Confirm before real employee data. |
| Breaks | Manual daily unpaid break; no inferred deduction. | Configure before definitive balances. |
| Leave effect | Manager chooses a configured treatment at approval. | Define actual leave types/treatments before live use. |
| Calendar | Belgian holiday proposals, manager-selected application/replacements and treatment; no inferred sector policy. | Confirm year coverage before definitive balances. |
| Manager's own requests | Another manager approves. | Assign at least two managers if managers also submit requests. |
| Dates | Whole-day leave; all-or-nothing decisions. | Confirm whether half-days are later needed. |
| History | Live recalculation and audit; no monthly locking or payroll settlement. | Revisit if used for payroll. |
| Hosting | Self-hosted Linux with HTTPS and backups. | Select a real host/domain before deployment. |

These open choices do not prevent implementation with synthetic data. No actual policy or contract is supplied by this document.
