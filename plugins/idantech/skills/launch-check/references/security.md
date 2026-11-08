# Security (checks 1 + 10)

Guide link for the report: https://idantech.co.il/guides/security-first-prompt

This is a **full audit of all files**, not only recent changes. Claude Code's
built-in `/security-review` looks at the pending diff — useful before each
commit, but it would miss problems in code written weeks ago. Mention that to
the user as an ongoing habit; it does not replace this pass.

In real tests of AI-built systems the most common serious findings were not
exotic: an admin password in a seed script and the README, missing login
rate-limiting, and authorization enforced only in the UI. Look there first.

## Secrets and keys (check 10)

Start from `scan_secrets.py` output, then confirm:
- No passwords, API keys, tokens or private keys in source, README, seed
  scripts, client bundles (`dist/`, `build/`, `.next/`, `public/`) or git history.
- `.env` is git-ignored and not tracked; `.env.example` holds placeholders only.
- AI provider calls (OpenAI, Anthropic, Gemini) and payment calls run on the
  server. A key in browser code is public — anyone can open DevTools → Sources.
- Supabase: the `anon` key in the client is fine **only** if RLS is enabled on
  every table; a `service_role` key in the client is critical.

A leaked key goes in the report as critical with the instruction to rotate it
at the provider. Don't delete it as a "fix".

## Authentication and sessions
- Passwords stored as bcrypt/argon2 hashes, minimum 8 characters.
- Login attempts are rate-limited (otherwise unlimited guessing).
- Login/registration errors don't reveal whether an email exists.
- Changing a password invalidates other sessions; session id rotates on login.
- Demo/seed users exist only in development, never in production data.

## Authorization
- Every server route checks identity, role and **data ownership** itself.
  Hiding a button in the UI is not authorization. Test the idea concretely:
  can user A fetch `/api/orders/123` belonging to user B by changing the id?
- State-dependent actions re-check conditions at save time (e.g. editing a
  submission after it was already graded).

## Input and output
- SQL uses parameters/ORM only — no string concatenation of user input.
- User content rendered without escaping (`dangerouslySetInnerHTML`, `v-html`,
  `innerHTML`, unescaped template output) → XSS.
- Error responses don't expose stack traces, SQL or internal paths in production.

## Uploads (if any)
- Allow-list of types, size checked before reading into memory, stored outside
  the public folder under random names, deleted when replaced or on failure.

## Transport and headers
- CSRF protection on state-changing requests, including login.
- `Content-Security-Policy` and `X-Frame-Options` / `frame-ancestors`.
- HTTPS in production; cookies `HttpOnly`, `Secure`, `SameSite`.

## Infrastructure
- The app connects to the database with a dedicated least-privilege user, not root,
  with a strong password.
- Dependencies: run `npm audit --omit=dev` (or the stack's equivalent) if the user
  approved it; report only high/critical advisories that reach production code.

## Manual test for the user (30 seconds)
Open a private/incognito window and paste the URL of an internal page
(dashboard, admin). If it opens without logging in — that's a finding.
