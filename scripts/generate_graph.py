#!/usr/bin/env python3
"""
Extract links + shared tags across docs/**.md into docs/assets/graph.json,
consumed by docs/assets/knowledge-graph.js on docs/graph.md.

Two edge kinds:
  - "link": an explicit markdown link from one page to another
  - "tag":  two pages share at least one front-matter tag (weight = count)

Run standalone (`python3 scripts/generate_graph.py`) or as part of the sync
pipeline — it only reads already-synced Markdown, so it has no Notion
dependency of its own.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
OUTPUT = DOCS_DIR / "assets" / "graph.json"

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s#]+)(?:#[^)\s]*)?\)")
FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TAG_LINE_RE = re.compile(r"^\s*-\s*(.+)$")
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

EXCLUDE = {"index.md", "tags.md", "graph.md", "recently-updated.md", "start-here.md", "glossary.md", "faq.md", "now.md"}


def load_page(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    tags = []
    m = FRONT_MATTER_RE.match(text)
    if m:
        in_tags = False
        for line in m.group(1).splitlines():
            if line.strip() == "tags:":
                in_tags = True
                continue
            if in_tags:
                tm = TAG_LINE_RE.match(line)
                if tm:
                    tags.append(tm.group(1).strip())
                    continue
                in_tags = False
        text = text[m.end():]
    title_match = TITLE_RE.search(text)
    title = title_match.group(1).strip() if title_match else path.stem
    links = []
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            rel = resolved.relative_to(DOCS_DIR.resolve()).as_posix()
        except ValueError:
            continue
        links.append(rel)
    return {"title": title, "tags": tags, "links": links}


def main() -> int:
    pages = {}
    for path in DOCS_DIR.rglob("*.md"):
        rel = path.relative_to(DOCS_DIR).as_posix()
        if path.name in EXCLUDE and "/" not in rel:
            continue
        pages[rel] = load_page(path)

    nodes = [{"id": rel, "title": p["title"], "tags": p["tags"]} for rel, p in sorted(pages.items())]

    edges = []
    seen = set()
    for rel, p in pages.items():
        for target in p["links"]:
            if target in pages and target != rel:
                key = tuple(sorted((rel, target))) + ("link",)
                if key not in seen:
                    seen.add(key)
                    edges.append({"source": rel, "target": target, "kind": "link"})

    tag_index = {}
    for rel, p in pages.items():
        for t in p["tags"]:
            tag_index.setdefault(t.lower(), []).append(rel)
    tag_pairs = {}
    for members in tag_index.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                key = tuple(sorted((members[i], members[j])))
                tag_pairs[key] = tag_pairs.get(key, 0) + 1
    for (a, b), weight in tag_pairs.items():
        key = (a, b, "tag")
        if key not in seen:
            seen.add(key)
            edges.append({"source": a, "target": b, "kind": "tag", "weight": weight})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=2, sort_keys=True), encoding="utf-8")
    print(f"docs/assets/graph.json  →  {len(nodes)} nodes, {len(edges)} edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
