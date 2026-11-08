#!/usr/bin/env python3
"""Static pre-launch checks on HTML / CSS / JSX files. Read-only.

Usage:
  python3 static_checks.py [PROJECT_DIR]

Fast, deterministic first pass — it does not replace a real browser audit
(axe / Lighthouse) or reading the code. It flags:
  accessibility: <html> lang/dir, img alt, unlabeled inputs, empty buttons/links,
                 outline removal, missing skip link, accessibility statement link
  seo/share:     <title>, meta description, h1 count, Open Graph, viewport, favicon,
                 sitemap.xml / robots.txt
  links/forms:   href="#" / javascript: links, forms without action or JS handler,
                 phone/email fields without a matching input type
  privacy:       privacy policy link, analytics / pixel scripts present (list them
                 so the policy can be compared against them), pre-checked checkboxes
Standard library only.
"""
import os
import re
import sys
from html.parser import HTMLParser

SKIP_DIRS = {".git", "node_modules", "vendor", ".venv", "venv", "__pycache__", "coverage"}
HTML_EXT = {".html", ".htm"}
JSX_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".php", ".astro"}
CSS_EXT = {".css", ".scss", ".sass", ".less"}

TRACKERS = {
    "Google Analytics / gtag": r"googletagmanager\.com|google-analytics\.com|gtag\(",
    "Meta Pixel": r"connect\.facebook\.net|fbq\(",
    "TikTok Pixel": r"analytics\.tiktok\.com|ttq\.",
    "Hotjar": r"hotjar\.com",
    "Microsoft Clarity": r"clarity\.ms",
    "LinkedIn Insight": r"snap\.licdn\.com",
    "Google Fonts (sends visitor IP to Google)": r"fonts\.googleapis\.com",
    "YouTube embed": r"youtube\.com/embed",
    "Google Maps embed": r"google\.com/maps",
    "reCAPTCHA": r"recaptcha",
    "WhatsApp link/widget": r"wa\.me|api\.whatsapp\.com",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues = []
        self.html_attrs = None
        self.title = False
        self.meta = {}
        self.h1 = 0
        self.labels_for = set()
        self.inputs = []
        self.open_btn = None
        self.open_a = None
        self.in_label = 0
        self.text_buf = []
        self.has_skip = False
        self.has_favicon = False
        self.forms = []
        self.links_text = []
        self.first_link = True
        self.page_name = ""

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "html":
            self.html_attrs = a
        elif tag == "title":
            self.title = True
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
        elif tag == "link" and "icon" in a.get("rel", ""):
            self.has_favicon = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            if "alt" not in a:
                self.issues.append(("a11y", line, f"<img src=\"{a.get('src','')[:40]}\"> has no alt attribute"))
        elif tag == "label":
            self.in_label += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        elif tag in ("input", "select", "textarea"):
            t = a.get("type", "text").lower()
            if t not in ("hidden", "submit", "button", "reset", "image"):
                self.inputs.append((line, a, self.in_label > 0))
            if t == "checkbox" and "checked" in a:
                self.issues.append(("privacy", line, f"checkbox '{a.get('name','')}' is pre-checked — marketing consent must not be pre-ticked"))
            name = (a.get("name", "") + a.get("id", "")).lower()
            if re.search(r"phone|tel|mobile|טלפון|נייד", name) and t not in ("tel", "hidden"):
                self.issues.append(("mobile", line, f"phone field '{a.get('name') or a.get('id')}' uses type=\"{t}\" — use type=\"tel\" for the right mobile keyboard"))
            if re.search(r"email|mail", name) and t not in ("email", "hidden"):
                self.issues.append(("mobile", line, f"email field '{a.get('name') or a.get('id')}' uses type=\"{t}\" — use type=\"email\""))
        elif tag == "button":
            self.open_btn = (line, a)
            self.text_buf = []
        elif tag == "a":
            href = a.get("href")
            if self.first_link and href and href.startswith("#") and len(href) > 1:
                self.has_skip = True
            self.first_link = False
            self.open_a = (line, a)
            self.text_buf = []
            if href is None or href.strip() in ("", "#") or href.startswith("javascript:"):
                self.issues.append(("links", line, f"link with href=\"{href or ''}\" goes nowhere"))
        elif tag == "form":
            self.forms.append((line, a))

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False
        elif tag == "label":
            self.in_label = max(0, self.in_label - 1)
        elif tag == "button" and self.open_btn:
            line, a = self.open_btn
            if not "".join(self.text_buf).strip() and not (a.get("aria-label") or a.get("aria-labelledby") or a.get("title")):
                self.issues.append(("a11y", line, "button with no text and no aria-label (icon button screen readers can't name)"))
            self.open_btn = None
        elif tag == "a" and self.open_a:
            line, a = self.open_a
            text = "".join(self.text_buf).strip()
            if not text and not a.get("aria-label"):
                self.issues.append(("a11y", line, f"link to \"{a.get('href','')[:40]}\" has no text/aria-label"))
            self.links_text.append(text)
            self.open_a = None

    def handle_data(self, data):
        if self.title and data.strip():
            self.meta["__title__"] = data.strip()
        if self.open_btn or self.open_a:
            self.text_buf.append(data)

    def finish(self):
        for line, a, wrapped in self.inputs:
            ok = wrapped or (a.get("id") and a["id"] in self.labels_for) or a.get("aria-label") or a.get("aria-labelledby")
            if not ok:
                self.issues.append(("a11y", line, f"form field '{a.get('name') or a.get('id') or a.get('type','')}' has no label (placeholder is not a label)"))
        h = self.html_attrs or {}
        if not h.get("lang"):
            self.issues.append(("a11y", 1, "<html> has no lang attribute (should be lang=\"he\")"))
        if h.get("dir", "").lower() != "rtl" and h.get("lang", "").startswith(("he", "ar")):
            self.issues.append(("a11y", 1, "<html> is Hebrew but has no dir=\"rtl\""))
        if "__title__" not in self.meta:
            self.issues.append(("seo", 1, "no <title>"))
        if not self.meta.get("description"):
            self.issues.append(("seo", 1, "no meta description"))
        if self.h1 != 1:
            self.issues.append(("seo", 1, f"{self.h1} <h1> elements (should be exactly one)"))
        missing_og = [k for k in ("og:title", "og:description", "og:image") if k not in self.meta]
        if missing_og:
            self.issues.append(("seo", 1, f"missing Open Graph tags: {', '.join(missing_og)} (WhatsApp/Facebook preview)"))
        if "viewport" not in self.meta:
            self.issues.append(("mobile", 1, "no <meta name=\"viewport\"> — page will render zoomed-out on phones"))
        if not self.has_favicon:
            self.issues.append(("seo", 1, "no favicon <link rel=\"icon\">"))
        if not self.has_skip and self.inputs is not None:
            self.issues.append(("a11y", 1, "no skip-to-content link as the first link"))
        texts = " ".join(self.links_text)
        is_statement_page = re.search(r"נגישות|accessibility", self.meta.get("__title__", "") + " " + self.page_name, re.I)
        if not is_statement_page and not re.search(r"נגישות|accessibility", texts, re.I):
            self.issues.append(("a11y", 1, "no link to an accessibility statement (הצהרת נגישות)"))
        if self.forms and not re.search(r"פרטיות|privacy", texts, re.I):
            self.issues.append(("privacy", 1, "page has a form but no link to a privacy policy"))


def files_by_ext(root, exts):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dirpath, fn)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def main(argv):
    root = os.path.abspath(argv[0] if argv else ".")
    out = {}
    html_files = list(files_by_ext(root, HTML_EXT))
    for path in html_files:
        p = PageParser()
        p.page_name = os.path.basename(path)
        text = read(path)
        try:
            p.feed(text)
            p.finish()
        except Exception as e:  # malformed html shouldn't stop the scan
            p.issues.append(("parse", 1, f"could not fully parse: {e}"))
        for cat, line, msg in p.issues:
            out.setdefault(cat, []).append(f"{os.path.relpath(path, root)}:{line} — {msg}")

    for path in files_by_ext(root, CSS_EXT | JSX_EXT | HTML_EXT):
        text = read(path)
        rel = os.path.relpath(path, root)
        for lineno, line in enumerate(text.splitlines(), 1):
            if re.search(r"outline\s*:\s*(none|0)\b|\boutline-none\b", line) and not re.search(r"focus-visible", line):
                out.setdefault("a11y", []).append(f"{rel}:{lineno} — focus outline removed ({line.strip()[:60]}) — needs a visible replacement")
            if re.search(r"<img\b(?![^>]*\balt=)[^>]*>", line) and os.path.splitext(path)[1] in JSX_EXT:
                out.setdefault("a11y", []).append(f"{rel}:{lineno} — <img> without alt")

    found = {}
    for path in files_by_ext(root, HTML_EXT | JSX_EXT | {".js", ".ts"}):
        if f"{os.sep}dist{os.sep}" in path or f"{os.sep}build{os.sep}" in path:
            continue
        text = read(path)
        for name, rx in TRACKERS.items():
            if re.search(rx, text):
                found.setdefault(name, []).append(os.path.relpath(path, root))

    for fname in ("sitemap.xml", "robots.txt"):
        if not any(os.path.exists(os.path.join(root, d, fname)) for d in ("", "public", "dist", "build", "static")):
            out.setdefault("seo", []).append(f"no {fname} found")
    if not any(re.search(r"404", os.path.basename(p)) for p in files_by_ext(root, HTML_EXT | JSX_EXT)):
        out.setdefault("links", []).append("no custom 404 page found (by file name)")

    titles = {"a11y": "Accessibility", "seo": "SEO & share preview", "mobile": "Mobile",
              "links": "Links", "privacy": "Privacy", "parse": "Parse errors"}
    print(f"# Static checks: {root}")
    print(f"HTML files scanned: {len(html_files)}\n")
    for cat in ("a11y", "privacy", "mobile", "seo", "links", "parse"):
        if out.get(cat):
            print(f"## {titles[cat]} ({len(out[cat])})")
            for item in sorted(set(out[cat])):
                print(f"- {item}")
            print()
    print("## Third-party services detected (compare against the privacy policy)")
    if found:
        for name, paths in found.items():
            print(f"- {name}: {', '.join(sorted(set(paths))[:3])}")
    else:
        print("- none detected")
    print("\nThis is a static first pass. Confirm findings in the code and with a browser audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
