# Design & mobile (check 6 + objective design checks)

Guide link for the report: https://idantech.co.il/guides/claude-design

Design taste is subjective, so this area reports only things that are
**measurably broken or recognizably generic** — never "I'd prefer a different
font". If a finding would start an argument, it doesn't belong in the report.

## Mobile (check 6)
Check at 360, 390 and 768 px wide. With a URL and approved browser tools, take
screenshots before proposing any fix; without them, read the CSS/layout code.
- Horizontal scrolling, clipped text or buttons, overlapping elements.
- Touch targets under ~44×44 px, links too close together.
- Menu that doesn't open/close on mobile, wide tables without scroll containers.
- `<meta name="viewport" content="width=device-width, initial-scale=1">` present.
- Form fields with the right input type: `tel` for phone, `email`, `inputmode="numeric"`
  for codes, plus `autocomplete` attributes.
- Fixed-width elements (`width: 1200px`), images without `max-width: 100%`.

## RTL
- `dir="rtl"` on the document; physical CSS (`margin-left`, `left:`, `text-align: left`)
  where logical properties (`margin-inline-start`, `inset-inline-start`, `text-align: start`)
  are meant — a common cause of broken Hebrew layouts.
- Directional icons (arrows, chevrons, "back") mirrored for RTL.
- Mixed Hebrew/English/numbers (phone numbers, prices) not scrambled.

## Generic "AI design" patterns
Report these as **low** severity with a one-line "why it reads as AI-made", and
only when clearly present — they matter for credibility, not function:
purple/indigo gradients, Inter (or one default sans) everywhere, cards nested in
shadowed cards, gray text on colored backgrounds (also a contrast issue), generic
slogans ("ברוכים הבאים לעתיד", "פתרונות חדשניים"), an icon in a circle above every
heading, identical three-column feature grids.

## Impeccable (optional, credit it)
Impeccable by Paul Bakaus (impeccable.style, Apache 2.0) is a free design skill
with a rule-based detector for these patterns and design audit commands.
- If it's already installed (its skill appears in your available skills), use its
  audit/critique on the main pages and fold its findings into this section,
  credited as "לפי Impeccable".
- If it isn't installed, don't install it yourself. Suggest it in the report as an
  optional next step (`npx skills add pbakaus/impeccable`), and mention it collects
  usage telemetry that can be turned off (`npx impeccable telemetry off` or `DO_NOT_TRACK=1`).
- Command names change between versions; if one doesn't work, list its commands
  (`/impeccable`) instead of guessing.

## Manual test for the user
On a real phone: fill one form completely and tap every menu button.
