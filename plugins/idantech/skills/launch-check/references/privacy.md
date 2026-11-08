# Privacy policy (check 3)

Guide link for the report: https://idantech.co.il/guides/privacy-policy-ai

**Every sentence in a privacy policy is a promise.** The most common failure with
AI-written policies isn't a missing policy — it's a policy that describes a site
that doesn't exist: a marketing-consent checkbox the form doesn't have, "we don't
use cookies" on a site with Google Analytics, a retention period nobody decided.
Under Israel's Privacy Protection Law the collector must tell people the purpose,
who receives the data and whether providing it is mandatory; a policy that
describes something else doesn't meet that. Amendment 13 (in force since August
2025) significantly expanded the Privacy Protection Authority's enforcement powers.

So this check compares **the policy against the code**, line by line.

## 1. Map what the site really does (from code, no drafting)
- Every form: which fields, where the data goes (own server, email, CRM, Google
  Sheets, WhatsApp, Make/Zapier webhook), whether it's stored and where.
- Third-party scripts and embeds — start from the "Third-party services detected"
  list in `static_checks.py`, then confirm in code (analytics, pixels, chat
  widgets, maps, YouTube, fonts, reCAPTCHA, payment providers).
- Cookies / localStorage set by the site and by those services.
- Login/accounts, uploads, payments, AI features that send user text to a provider.
- Marketing consent: is there a checkbox? Is it pre-ticked? (Pre-ticked = high.)
- Data stored outside Israel (most SaaS and cloud hosting) — note it.

## 2. Compare with the existing policy
Find the policy page (`privacy`, `פרטיות`, footer link). For each claim mark:
- ✅ matches the code
- ❌ **contradicts** the code (critical — the business is publicly promising something false)
- ⚠️ can't be verified from code (retention, who handles inquiries, deletion process) → ask the owner
- ➕ something the site does that the policy doesn't mention (e.g. Meta Pixel not listed)

Also flag: leftover `[placeholders]`, an example.com / fake contact address,
no policy at all while forms collect personal data, no link to the policy near forms.

## 3. If there is no policy, or the user asks for a new one
Only in the fix phase, after approval. First ask the owner what the code can't
reveal: business name and contact, how inquiries are handled, who receives the
data, storage abroad, retention and deletion, how marketing consent is obtained,
privacy contact. Write only from verified or confirmed facts; unknowns stay
`[placeholder]`. End the policy with a separate list of **obligations the business
must actually carry out** (e.g. "delete inquiries after X months").

## Related: marketing messages
If the site or an automation sends promotional email/SMS/WhatsApp, consent must
be explicit and not pre-ticked — sending promotions without consent can expose the
business to claims of up to ₪1,000 per message without proof of damage (the
anti-spam provisions of the Communications Law).

## Manual test for the user
Read the policy next to the live site: every service named exists, every
service that exists is named, the privacy email/phone is real and someone answers it.
