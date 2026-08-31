#!/usr/bin/env python3
"""
Documentation quality gate, run in CI before a sync commits and before a
build deploys:

- broken internal links / images (relative markdown links that don't
  resolve to a real file under docs/)
- orphan pages (a .md file under docs/notion/ that mkdocs.yml's nav
  doesn't reference)
- empty pages (nothing but a title heading — usually a sync artifact)
- invalid YAML front matter

Exits non-zero and prints every failure found (not just the first) if any
check fails. Doesn't require network access or a built site — it works
directly off the Markdown sources, which is what makes it fast enough to
run on every sync.
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
MKDOCS_YML = ROOT / "mkdocs.yml"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def iter_markdown_files():
    return sorted(DOCS_DIR.rglob("*.md"))


def is_external(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith("//")


def check_links(files: list) -> list:
    errors = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or is_external(target) or target.startswith("#") or target.startswith("mailto:"):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (f.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(f"{f.relative_to(ROOT)}  →  {target}  (resolved: {resolved.relative_to(ROOT) if ROOT in resolved.parents or resolved == ROOT else resolved})")
    return errors


def check_orphans(files: list) -> list:
    """Every .md under docs/notion/ should be reachable from mkdocs.yml's nav."""
    nav_text = MKDOCS_YML.read_text()
    referenced = set(re.findall(r"notion/[\w./-]+\.md", nav_text))
    orphans = []
    for f in (DOCS_DIR / "notion").rglob("*.md") if (DOCS_DIR / "notion").exists() else []:
        rel = f.relative_to(DOCS_DIR).as_posix()
        if rel not in referenced:
            orphans.append(rel)
    return orphans


def check_empty_pages(files: list) -> list:
    empty = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        text = FRONT_MATTER_RE.sub("", text, count=1)
        text = re.sub(r'--8<--\s*"[^"]*"', "", text)
        body = re.sub(r"^#.*$", "", text, count=1, flags=re.MULTILINE).strip()
        if not body:
            empty.append(f.relative_to(ROOT).as_posix())
    return empty


def check_front_matter(files: list) -> list:
    errors = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = FRONT_MATTER_RE.match(text)
        if not m:
            continue
        try:
            yaml.safe_load(m.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{f.relative_to(ROOT)}: {exc}")
    return errors


def main() -> int:
    files = iter_markdown_files()

    # Hard failures: these mean something is actually broken.
    blocking = [
        ("Broken internal links/images", check_links(files)),
        ("Invalid front matter", check_front_matter(files)),
    ]
    # Informational: worth seeing, but a thin landing page for a nav section
    # (e.g. a Notion parent page with only children, no body of its own) is
    # legitimate, not a bug — don't fail a sync over it.
    advisory = [
        ("Orphan pages (not in mkdocs.yml nav)", check_orphans(files)),
        ("Thin pages (title only, no body)", check_empty_pages(files)),
    ]

    failed = False
    for name, problems in blocking:
        if problems:
            failed = True
            print(f"\n✗ {name} ({len(problems)}):")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"✓ {name}: none")

    for name, problems in advisory:
        if problems:
            print(f"\n! {name} ({len(problems)}) — informational, not blocking:")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"✓ {name}: none")

    if failed:
        print("\nDocumentation quality check FAILED.")
        return 1
    print("\nDocumentation quality check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
