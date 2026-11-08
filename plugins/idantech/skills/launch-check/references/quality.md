# Quality: forms, speed, SEO, links (checks 4, 7, 8, 9)

Guide link for the report: https://idantech.co.il/guides/launch-checks

## 4. Forms that actually work
A form that shows "תודה, נחזור אליכם" and sends nothing loses every lead
silently — AI builds this surprisingly often when no backend was specified.
For each form trace the submit handler to its destination:
- Does the data reach a real destination (API route, email service, CRM, webhook)?
- **Fake success:** success message shown without a request, or regardless of the
  response (`catch` that still shows success, no `res.ok` check) → high.
- On failure the user sees an error and their input is kept.
- Server-side validation exists (client validation alone is bypassable).
- Basic spam protection: honeypot field, rate limit, or captcha.
- Don't connect a new service in the fix phase without asking.
Manual test: submit every form with your own details and confirm the message arrives.

## 7. Load speed
With approval and a URL: Lighthouse **mobile** on a production build (not the dev
server — dev builds are unminified and misleading). Report the score first.
From code, look for:
- Large images without WebP/AVIF, without `width`/`height`, without `loading="lazy"`
  below the fold; hero images over ~300KB.
- Render-blocking fonts (no `font-display: swap`, many weights), unused CSS/JS libraries.
- No compression/caching headers; dozens of requests for small assets.
After approved fixes, re-run and show before/after.
Manual test: Chrome → F12 → Lighthouse → Mobile → Analyze.

## 8. SEO and share preview
- Unique `<title>` and meta description per page, exactly one `h1`.
- `lang="he"` + `dir="rtl"`.
- Open Graph: `og:title`, `og:description`, `og:image` (1200×630, absolute URL),
  plus `twitter:card`. Without them a WhatsApp share shows a bare link.
- Favicon, `sitemap.xml`, `robots.txt` (and robots must not block the whole site
  — a leftover `Disallow: /` from staging is critical for SEO).
- SPA (React/Vite without SSR): check whether crawlers get real content or an empty
  `<div id="root">`; suggest prerendering/SSR for marketing pages if so.
Manual test: send the link to yourself on WhatsApp — image, title and description?

## 9. Broken links
- Every internal link, image path and `#anchor` resolves (check against the routes
  and files that exist).
- `tel:` and `mailto:` are correct (Israeli numbers as `tel:+9725…`).
- Empty `href="#"` / `javascript:void(0)` buttons that do nothing.
- A styled 404 page exists and the server returns status 404 for it.
Manual test: click every menu and footer item, then open a made-up URL.
