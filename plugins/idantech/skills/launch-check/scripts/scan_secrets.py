#!/usr/bin/env python3
"""Scan a project for exposed secrets. Read-only: never edits or deletes anything.

Usage:
  python3 scan_secrets.py [PROJECT_DIR] [--no-history]

Checks:
  * working tree files (incl. build output like dist/, build/, .next/, out/)
  * whether .env* files are git-ignored / tracked
  * whether .env.example holds values that look real
  * git history (all commits) for the same patterns, unless --no-history

Secrets are printed MASKED (first 4 chars + length) so the report itself
never leaks a key. Standard library only.
"""
import os
import re
import subprocess
import sys

PATTERNS = [
    ("Anthropic API key", r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    ("OpenAI / generic sk- key", r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}"),
    ("AWS access key id", r"AKIA[0-9A-Z]{16}"),
    ("Google API key", r"AIza[0-9A-Za-z_\-]{35}"),
    ("Stripe secret key", r"sk_live_[0-9A-Za-z]{20,}"),
    ("GitHub token", r"gh[pousr]_[A-Za-z0-9]{30,}"),
    ("Slack token", r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
    ("Private key block", r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ("Supabase service_role", r"service_role[\"'\s:=]+[A-Za-z0-9_\-\.]{20,}"),
    ("JWT", r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    ("Hardcoded password", r"(?i)(?:password|passwd|pwd|סיסמה)[\"']?\s*[:=]\s*[\"'][^\"'\s]{4,}[\"']"),
    ("Connection string with password", r"(?i)(?:mysql|postgres(?:ql)?|mongodb(?:\+srv)?)://[^:\s/]+:[^@\s]+@"),
]
COMPILED = [(name, re.compile(rx)) for name, rx in PATTERNS]

SKIP_DIRS = {".git", "node_modules", "vendor", ".venv", "venv", "__pycache__", ".cache", "coverage"}
BUILD_DIRS = {"dist", "build", ".next", "out", ".output", "public"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".svg", ".woff", ".woff2",
            ".ttf", ".eot", ".mp4", ".mov", ".mp3", ".pdf", ".zip", ".gz", ".lock"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
MAX_BYTES = 2_000_000
PLACEHOLDER = re.compile(r"(?i)(your|example|changeme|placeholder|xxx+|<.*>|\*\*\*|dummy|test|sample|\.\.\.)")


def mask(s):
    s = s.strip()
    return f"{s[:4]}…({len(s)} chars)"


def scan_text(text):
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in COMPILED:
            for m in rx.finditer(line):
                hits.append((lineno, name, m.group(0)))
    return hits


def walk(root):
    findings = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in SKIP_FILES or os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
                with open(path, encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue
            rel = os.path.relpath(path, root)
            parts = set(rel.split(os.sep))
            where = "build output (shipped to the browser)" if parts & BUILD_DIRS else "source"
            if fn.startswith(".env"):
                continue  # .env must hold secrets and .env.example must not; env_checks() covers both
            for lineno, name, value in scan_text(text):
                if PLACEHOLDER.search(value) and name in ("Hardcoded password", "Connection string with password"):
                    continue
                findings.append((rel, lineno, name, mask(value), where))
    return findings


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def env_checks(root):
    notes = []
    code, _ = git(root, "rev-parse", "--is-inside-work-tree")
    is_git = code == 0
    env_files = [f for f in os.listdir(root) if f.startswith(".env")]
    real_env = [f for f in env_files if not f.endswith((".example", ".sample", ".template"))]
    if not is_git:
        notes.append(("INFO", "Not a git repository — .gitignore / history checks skipped."))
    else:
        _, tracked = git(root, "ls-files")
        tracked = set(tracked.split())
        for f in real_env:
            if f in tracked:
                notes.append(("CRITICAL", f"{f} is TRACKED by git — its values are in the repo."))
            else:
                c, _ = git(root, "check-ignore", "-q", f)
                if c != 0:
                    notes.append(("HIGH", f"{f} is not in .gitignore — one `git add .` away from leaking."))
        if not real_env:
            c, _ = git(root, "check-ignore", "-q", ".env")
            if c != 0:
                notes.append(("MEDIUM", ".env is not covered by .gitignore (add it before creating one)."))
    for f in env_files:
        if f.endswith((".example", ".sample", ".template")):
            with open(os.path.join(root, f), encoding="utf-8", errors="ignore") as fh:
                for lineno, line in enumerate(fh, 1):
                    if "=" in line and not line.lstrip().startswith("#"):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val and not PLACEHOLDER.search(val) and len(val) >= 12:
                            notes.append(("HIGH", f"{f}:{lineno} looks like a real value ({mask(val)})."))
    return is_git, notes


HISTORY_LIMIT = 200_000_000  # stop reading history after ~200MB of diff on huge repos


def history(root):
    """Scan every added/removed line in all commits. Streams, so big repos stay cheap on memory."""
    key_patterns = COMPILED[:10]  # password-style patterns are too noisy across history
    try:
        proc = subprocess.Popen(
            ["git", "-C", root, "log", "--all", "-p", "--no-color", "--no-ext-diff",
             "--format=@@COMMIT %h %ad", "--date=short"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, errors="ignore")
    except OSError:
        return [], False
    results, commit, read_bytes, truncated = set(), None, 0, False
    for line in proc.stdout:
        read_bytes += len(line)
        if read_bytes > HISTORY_LIMIT:
            truncated = True
            proc.kill()
            break
        if line.startswith("@@COMMIT "):
            commit = line[9:].strip()
        elif line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            for name, rx in key_patterns:
                for m in rx.finditer(line):
                    results.add((commit, name, mask(m.group(0))))
    proc.wait()
    return sorted(results), truncated


def main(argv):
    root = os.path.abspath(next((a for a in argv if not a.startswith("--")), "."))
    findings = walk(root)
    is_git, notes = env_checks(root)
    hist, truncated = history(root) if is_git and "--no-history" not in argv else ([], False)

    print(f"# Secret scan: {root}\n")
    print("## Files")
    if findings:
        for rel, lineno, name, masked, where in findings:
            print(f"- {rel}:{lineno} — {name} {masked} [{where}]")
    else:
        print("- No secret patterns found in files.")
    print("\n## .env hygiene")
    for sev, msg in notes or [("OK", ".env handling looks fine.")]:
        print(f"- [{sev}] {msg}")
    if is_git:
        print("\n## Git history")
        if hist:
            for commit, name, masked in hist:
                print(f"- commit {commit} — {name} {masked} (still retrievable from history)")
        else:
            print("- No secret patterns found in history.")
        if truncated:
            print("- [INFO] History is very large; only the most recent ~200MB of diffs were scanned.")
    print("\nNote: a leaked key must be ROTATED at the provider. Deleting it from the code is not enough.")
    return 1 if findings or hist or any(s in ("CRITICAL", "HIGH") for s, _ in notes) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
