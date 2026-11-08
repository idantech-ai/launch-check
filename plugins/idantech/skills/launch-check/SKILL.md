---
name: launch-check
description: Pre-launch audit for a website or web app built with AI — security, exposed API keys, accessibility (Israeli standard ת"י 5568 / WCAG 2.1 AA), privacy policy vs. what the code actually collects, design and mobile, forms, speed, SEO and broken links. Produces one Hebrew report ranked by severity and changes nothing until the user approves fixes. Use whenever the user is about to go live, deploy, launch or hand over a site, asks to "check everything", "run the checks", "בדיקות לפני עלייה לאוויר", "תבדוק את האתר", or asks whether their site is safe, accessible or legally OK — even if they name only one of these areas.
---

# Launch Check — בדיקות לפני עלייה לאוויר

A site that "works" can still leak an API key, be unusable without a mouse,
or publish a privacy policy that promises things the site doesn't do. Each of
those can cost real money in Israel (accessibility lawsuits without proof of
damage, Privacy Protection Authority enforcement under Amendment 13, spam-law
claims per message). This skill finds those problems before launch.

The working principle is **report first, fix only after approval**. The user
owns the decisions — some fixes change brand colors, some need a key rotated
at a provider, some need facts only the business owner knows. So the audit
phase never edits project files.

## Language

Talk to the user in Hebrew from the first message: progress updates, questions,
the report and the fix summaries. Only code, file paths and commands stay in
English. Users often screen-record this flow, so a single English status line
in the middle stands out.

## Scope from the command

The user may pass an area: `/idantech:launch-check security` (or אבטחה), `accessibility`
(נגישות), `privacy` (פרטיות), `design` (עיצוב), `quality` (טפסים, מהירות, SEO,
קישורים). Run only that area. With no area, run all of them.

## Step 1 — Understand the project (1–2 minutes, no edits)

Read `package.json` / `composer.json` / `requirements.txt`, the folder layout and
the routes. Establish:
- Static site, SPA, or app with a server? Which framework? Where does the build go?
- Is there login / user data / file upload / payments / AI calls?
- Which forms exist, and where does each one send data?
- Is there a running URL (dev server or deployed)? Browser-based checks need one.

Tell the user in two or three lines what you found and which areas apply
(e.g. "no login, so authorization checks are N/A").

## Step 2 — Fast automated pass

Run the bundled scripts (standard-library Python, nothing to install, read-only):

```bash
python3 -I <skill-dir>/scripts/scan_secrets.py <project-dir>
python3 -I <skill-dir>/scripts/static_checks.py <project-dir>
python3 -I <skill-dir>/scripts/contrast.py "#TEXT" "#BG"              # brand color is the text
python3 -I <skill-dir>/scripts/contrast.py "#TEXT" "#BG" --adjust-bg  # brand color is the background (buttons)
```

Run `contrast.py` for each text/background pair you find in the CSS or theme.
Pick `--adjust-bg` when the brand color is the fill (a white-on-orange button),
so the suggested fix keeps the brand hue instead of turning the text gray.

`scan_secrets.py` masks every secret it prints — keep it that way in the report.
Never print a full key, password or token anywhere.

Treat script output as leads, not verdicts: open the file and confirm each one
before it goes in the report. Drop false positives silently.

**External tools need consent.** Tools like `npx @axe-core/cli`, `npx lighthouse`,
`npm audit` (which sends the dependency list to the npm registry), or Impeccable
download and run code. Before the first one, list the tools you'd like to run in
one message and ask once. If the user declines, continue with the scripts and
code reading and mark the browser-only checks as "needs manual test".

## Step 3 — Deep checks by area

Read only the reference files for the areas in scope:

| Area | Reference | Covers (launch-check numbers) |
|---|---|---|
| Security | `references/security.md` | 1 security, 10 exposed keys |
| Accessibility | `references/accessibility.md` | 2 accessibility, 5 accessibility statement |
| Privacy | `references/privacy.md` | 3 privacy policy vs. reality |
| Design & mobile | `references/design.md` | 6 mobile, objective design checks, Impeccable |
| Quality | `references/quality.md` | 4 forms, 7 speed, 8 SEO & share, 9 links |

Only report what you verified in the code or in a tool's output. "Might be
vulnerable" without a concrete file and reason is noise — leave it out or put
it under "to check manually".

## Step 4 — The report

Write the report in Hebrew using `assets/report-template.md`, save it as
`launch-report.md` in the project root, and show the summary table plus the
critical/high findings in the chat. Severity scale for every area:

- **קריטי** — exploitable now or exposes the owner to a claim now (leaked live key, admin password in a public repo, no accessibility at all on a public business site, policy that contradicts the site)
- **גבוה** — serious, should block launch (no server-side authorization, form that silently loses leads, pre-ticked marketing consent)
- **בינוני** — fix before or shortly after launch
- **נמוך** — polish and hardening

Each critical/high finding gets the full block from the template: what, where
(file:line), why it matters in one sentence, the proposed fix, and the matching
guide link. Medium and low findings fit on one line each — a long report buries
the findings that matter. Merge findings with one root cause (a tracked `.env`
and a real value in `.env.example` are one problem). Then list the 30-second
manual tests that only a human can do, and what wasn't checked and why.

The report is a map of the site's weak spots. Tell the user not to commit it to
a public repo (suggest adding `launch-report.md` to `.gitignore` in the fix phase).

End with a clear stop: ask which findings to fix ("הכל", "רק קריטי וגבוה", or
numbers). Do not continue until the user answers.

## Step 5 — Fix after approval

- Fix in severity order, one sentence per fix explaining what changed.
- Change nothing beyond what the finding requires.
- **Leaked keys:** never "fix" by deleting the key from code alone. Move it to
  an env variable / server side, and tell the user to rotate it at the provider
  (the old key is still in git history and possibly in a build already served).
- **Brand colors:** use the closest passing shade from `contrast.py`, not a new color.
- **Privacy policy / accessibility statement text:** facts the code can't reveal
  (retention period, coordinator name, phone) become `[placeholder]` — never invent them.
- **Forms:** don't connect a new third-party service without asking.
- Afterwards re-run the same checks and show a before/after table
  (e.g. "קריטי: 3 → 0"). That table is the proof the fixes worked.

## Limits to state in the report

Automated checks and an AI review are a strong first line, not a certificate.
Formal accessibility compliance is determined by a certified accessibility
consultant (יועץ נגישות מורשה), and a privacy policy for a business with
sensitive or large-scale data should be reviewed by a lawyer. Say this once,
plainly, at the end of the report — not as a disclaimer on every finding.
