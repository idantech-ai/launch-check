# Accessibility (checks 2 + 5)

Guide link for the report: https://idantech.co.il/guides/accessibility-claude

Target: **WCAG 2.1 Level AA**, which Israel adopts as ת"י 5568 (referenced by
regulation 35 of the accessibility regulations for services). A non-compliant
public business site can be sued without proof of damage, so on a business
site accessibility findings are rarely "low".

AI-built sites usually fail in the same few places: a brand color that fails
contrast, focus outlines removed for looks, dialogs that don't take focus,
icon buttons with no name, and no accessibility statement. Check those first.

## Automated
Start from `static_checks.py`. If the user approved browser tools and there is
a URL: `npx @axe-core/cli <url>` and/or Lighthouse accessibility. A score is a
starting point, not proof of compliance — always do the manual checks below.

## What to verify in the code
- **Document:** `<html lang="he" dir="rtl">`, one `h1`, logical heading order,
  `header`/`nav`/`main`/`footer` landmarks, skip link to main content.
- **Contrast:** 4.5:1 normal text, 3:1 large text (≥24px, or ≥18.66px bold) and UI
  components (button borders, input outlines, icons). Run `contrast.py` on every
  text/background pair from the CSS/Tailwind config, including text over images
  and gray-on-color (use `--adjust-bg` when the brand color is the fill). For
  failures, report the closest passing shade it gives — the brand stays recognizable.
- **Keyboard:** everything clickable is a real `button`/`a` (or has role +
  tabindex + key handlers). `div onClick` is a finding. Focus is always visible —
  `outline: none` / `outline-none` without a `:focus-visible` replacement is a finding.
- **Dialogs, drawers, menus:** focus moves in on open, stays trapped, Esc closes,
  focus returns to the trigger.
- **Images:** informative → descriptive alt; decorative → `alt=""`.
- **Forms:** visible `label` per field (placeholder is not a label), errors linked
  with `aria-describedby` and announced, required fields marked in text not color only.
- **Icon buttons:** `aria-label` naming action + item ("הוספת סלט קיסר לסל", not "הוסף").
- **Dynamic messages** ("נוסף לסל", form success/failure) in an `aria-live` region.
- **Motion:** animations respect `prefers-reduced-motion`.
- **Accessibility plugins/overlays** (toolbar widgets): note that they change the
  display but don't fix the code, so they don't make the site compliant by themselves.

## Accessibility statement (check 5)
A Hebrew page "הצהרת נגישות", linked from the footer on **every** page, stating:
the standard and level, what was actually made accessible, known limitations,
and contact details of an accessibility coordinator (name, phone, email).
If missing, offer to create it in the fix phase with `[placeholders]` for the
coordinator details and the date of the last check — never invent them.

## Manual tests for the user (about two minutes)
1. Tab through the whole page only with the keyboard: is focus always visible?
   Can you open a dialog, use it, close it with Esc, and submit a form?
2. Contrast: Chrome → right-click text → Inspect → click the color swatch;
   DevTools shows the ratio and AA pass/fail.
3. Screen reader: Mac `Cmd+F5` (VoiceOver), Windows NVDA (free). Can you tell
   what every button does without looking?
4. Lighthouse → Accessibility in Chrome DevTools.
