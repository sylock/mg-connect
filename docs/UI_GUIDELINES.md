# UI guidelines

Version 0.3 · 28 September 2026

The user requires a beautiful, responsive and colourful web application. The selected implementation is Django templates + Tailwind CSS + daisyUI + HTMX, delivered as a PWA. The palette and layout details below are concrete design defaults, not a claim that rendered screens have already been approved or built.

## Visual direction

Warm, contemporary and polished, with generous spacing, clear typography and useful colour. Build a recognisable salon team application. Keep the interface compact enough for daily operations, avoiding decorative charts and empty oversized panels. Do not reproduce Connecteam branding or assets.

Use a custom daisyUI theme with shared semantic tokens, centralised in one CSS source. Every page uses the same theme. Start with a light theme; dark mode is deferred.

| Token | Suggested colour | Use |
| --- | --- | --- |
| Canvas | #FAF7F2 | Warm ivory page background. |
| Surface | #FFFFFF | Cards, forms and dialogs. |
| Text | #27232B | Main charcoal text. |
| Muted text | #625A66 | Secondary labels, still readable. |
| Primary | #6D365F | Plum primary actions and active navigation, white text. |
| Accent | #F38F7D | Coral highlights with dark text; not white small text. |
| Border | #DCD4DE | Dividers and control outlines. |
| Focus | #1D4ED8 | Visible keyboard focus ring. |

Use a readable system sans-serif stack initially, avoiding external font requests. Body text is normally 16 px; form inputs must remain comfortable on phones. Use tabular numerals for times and signed differences. Cards use moderate 12–16 px rounding, subtle borders/shadows and an 8 px spacing rhythm.

## Event colours and state badges

Colour identifies event type; text and icons carry meaning too. Status badges are separate from event colours so “leave” is not mistaken for “approved”. Verify contrast on actual rendered components rather than assuming the palette guarantees accessibility.

| Event | Tint | Text/accent | French label |
| --- | --- | --- | --- |
| Work | #DBEAFE | #1E40AF | Travail |
| Leave | #CCFBF1 | #115E59 | Congé |
| Holiday | #FEF3C7 | #92400E | Jour férié |
| Other | #EDE9FE | #5B21B6 | Autre |
| Rest | #F1F5F9 | #475569 | Repos |

Statuses: Brouillon, Publié, En attente, Accepté, Refusé, Annulé, Incomplet and Provisoire. Always show a text label. Positive/negative hour differences include +/− and a descriptive heading; avoid treating every negative difference as a disciplinary warning.

## Navigation and responsive layout

Desktop (approximately 1024 px and above): a restrained left sidebar with Accueil, Agenda, Succès, Congés and Rapports; managers also see Gestion. Main content uses available width; planning may be wider than ordinary forms.

Mobile: bottom navigation for Accueil, Agenda, Pointer and Plus; Plus exposes Succès, Congés, Rapports and authorised manager actions. Respect device safe areas and reserve content space above the fixed bar. All business features remain accessible on mobile, including monthly editing and publication.

Use content-driven responsive breakpoints; verify representative widths 360, 768 and 1440 px. No whole-page horizontal overflow. Forms become one column. Tables may scroll inside a labelled container when needed, but mobile agenda defaults to a readable date/employee list.

## Screens and behaviours

### Home and clocking

Show today's date, current clock state, today's planned hours and a prominent Arrivée or Départ action. Add clear actions Déclarer un succès and Demander un congé. Manager pending approvals can appear as a small count linked to the approval screen. Avoid ranking employees by default.

A clock action shows a pending indicator, then server-confirmed time and state. A network failure says the action is not confirmed; it never shows a success tick before the server commits. Retain the request token for safe retry.

### Shared agenda and manager planning

Desktop: employee rows and day columns with clear month navigation, sticky employee names/date header where practical, event chips and an explicit legend. Offer a week view to reduce horizontal density; a full month may scroll inside its own container. Mobile: grouped daily cards with employee filters and an event details panel.

Display the current view prominently: Planning publié or Aperçu du brouillon. In manager mode show draft state separately from the version currently visible to employees. Include last publication date/version and explicit actions Publier and Repasser en brouillon. Reopening retains the last public snapshot as specified in PLANNING.md.

Selecting a date/employee opens an accessible form or dialog: event type, work times, planned break, comment visibility and relevant leave/holiday controls. Drag-and-drop is optional and deferred; every edit must be possible with ordinary buttons, touch and keyboard. Generation/regeneration previews must explain which dates would change and protect manual edits.

Approved leave overlays display as Congé, without private motives. Show a marker when the agenda includes leave approved after the last work-plan publication. Missing published work says Horaire non publié, distinct from Repos.

### Achievements and leave

Use compact cards with date, category, state and permitted evidence preview. New achievement form supports link/image proof. New leave form supports one date, a range or non-contiguous dates and a reason. Do not expose private proof or leave reasons through shared cards.

Manager review places useful details near Accepter/Refuser. Refusal prompts for its reason. Avoid ambiguous one-tap irreversible actions; present a review step for publication, void/cancellation and bulk regeneration.

### Reports

Keep Actual attendance and Planned-versus-actual as distinct report tabs, with Achievements as another report. Shared filter controls: month/year, year, range or specific dates; employee or whole team; apply/reset actions with persistent selected values.

Desktop comparisons use aligned columns. Mobile comparisons use per-employee cards with labelled values. Show Prévu, Réalisé, Écart au planning, Attendu contractuel ajusté and Écart contractuel as separate quantities. Include absence adjustments and baseline contract details in an expandable breakdown. The same dates and formulas apply at every viewport width.

Show missing/incomplete/provisional data next to affected totals, with a short explanation and authorised correction link. Do not hide that a figure excludes today or future dates. Zero, unavailable and no records must have different representations.

### Comments

The visibility control offers Équipe and Privé — gérants, with a short explanation. Private reminders default to the private choice. The UI must not equate hidden text with access control; private text must be absent from unauthorised responses. Day comments work even without an event. Comment editing and event detail views respect publication and audit rules.

## Reusable components

Implement Django partials for app shell, page heading, primary/secondary/destructive buttons, labelled input, field error, filter bar, event chip, status badge, employee card, duration value, empty state, loading indicator, confirmation dialog and toast/live message. Use daisyUI primitives consistently; avoid a separate design for each page.

Prefer native semantic controls. Dialogs support focus trapping, Escape where safe and return focus to the trigger. Calendar selection has a keyboard-accessible alternative; a coloured grid alone is insufficient. Icons supplement text and use a single locally served compatible open-source set or simple inline trusted SVG assets.

## Accessibility and quality

Aim for WCAG 2.2 AA for the delivered flows: sufficient text/control contrast, visible focus, proper headings/labels, keyboard operation and errors linked to fields. Target touch controls at least 44×44 CSS px, allow text zoom, and honour reduced-motion preferences. Test long French labels and names. Do not announce compliance merely because a component library was used.

Every asynchronous action has loading, success, empty, validation-error, conflict, expired-session and network-error states as applicable. Preserve entered data when recoverable; a calendar update should not jump unpredictably or lose filters. After HTMX swaps, restore focus appropriately and announce significant status changes.

## Visual acceptance

Using synthetic data, capture and inspect desktop/mobile screens for home/clocking, shared agenda, manager draft editor, leave approval, achievement form and combined report. Check the same design tokens across screens; clear publication labels; no leaked private text; no full-page overflow; no clipped fixed navigation; and clean keyboard interaction.

The delivery is not visually complete until actual rendered screens have been inspected. Record which viewports and real devices were checked. Documentation alone is not a visual test.
