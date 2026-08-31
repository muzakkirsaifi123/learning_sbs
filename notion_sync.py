#!/usr/bin/env python3
"""
Sync Notion pages into MkDocs docs/notion/ folder as Markdown files.
Automatically updates the Notion section in mkdocs.yml.

Usage:
  NOTION_TOKEN=ntn_xxx NOTION_PAGE_ID=1fd9f2a93248826a83de816c57fc66b8 python3 notion_sync.py
"""

import os
import re
import sys
import logging
from pathlib import Path

logging.getLogger("notion_client").setLevel(logging.ERROR)

try:
    from notion_client import Client
except ImportError:
    print("ERROR: notion-client not installed. Run: pip install notion-client")
    sys.exit(1)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID", "")

DOCS_DIR = Path(__file__).parent / "docs" / "notion"
MKDOCS_YML = Path(__file__).parent / "mkdocs.yml"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text or "untitled"


def rich_text_to_md(rich_texts: list) -> str:
    result = ""
    for rt in rich_texts:
        text = rt.get("plain_text", "")
        ann = rt.get("annotations", {})
        href = rt.get("href")
        if ann.get("code"):
            text = f"`{text}`"
        if ann.get("bold"):
            text = f"**{text}**"
        if ann.get("italic"):
            text = f"*{text}*"
        if ann.get("strikethrough"):
            text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        result += text
    return result


def get_all_blocks(client: Client, block_id: str) -> list:
    blocks = []
    cursor = None
    while True:
        kwargs = {"block_id": block_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = client.blocks.children.list(**kwargs)
        blocks.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks


# Maps Notion callout emojis → MkDocs admonition types
_CALLOUT_MAP = {
    "💡": "tip",    "🔥": "warning",  "⚠️": "warning",  "🚨": "danger",
    "❌": "failure", "✅": "success",  "ℹ️": "info",     "📝": "note",
    "🧠": "abstract","📌": "tip",     "🎯": "example",   "💬": "quote",
    "🤔": "question","👉": "tip",     "📢": "info",      "🔑": "tip",
    "⛔": "danger",  "🛑": "danger",  "📣": "info",      "🏆": "success",
}


def block_to_md(block: dict, client: Client, depth: int = 0) -> str:
    btype = block.get("type", "")
    data = block.get(btype, {})
    indent = "  " * depth
    lines = []

    if btype == "paragraph":
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f"{indent}{text}\n")

    elif btype in ("heading_1", "heading_2", "heading_3"):
        level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[btype]
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f"\n{level} {text}\n")

    elif btype == "bulleted_list_item":
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f"{indent}- {text}\n")
        if block.get("has_children"):
            for child in get_all_blocks(client, block["id"]):
                lines.append(block_to_md(child, client, depth + 1))

    elif btype == "numbered_list_item":
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f"{indent}1. {text}\n")
        if block.get("has_children"):
            for child in get_all_blocks(client, block["id"]):
                lines.append(block_to_md(child, client, depth + 1))

    elif btype == "code":
        lang = data.get("language", "plain text")
        if lang == "plain text":
            lang = "text"
        text = rich_text_to_md(data.get("rich_text", []))
        caption = rich_text_to_md(data.get("caption", []))
        caption_line = f"\n_{caption}_\n" if caption else ""
        lines.append(f"```{lang}\n{text}\n```{caption_line}\n")

    elif btype == "quote":
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f"> {text}\n")

    elif btype == "callout":
        text = rich_text_to_md(data.get("rich_text", []))
        icon = data.get("icon", {}).get("emoji", "")
        admonition = _CALLOUT_MAP.get(icon, "note")
        title = icon if icon else ""
        header = f'!!! {admonition} "{title}"' if title else f"!!! {admonition}"
        lines.append(f"{header}\n    {text}\n")
        if block.get("has_children"):
            for child in get_all_blocks(client, block["id"]):
                child_md = block_to_md(child, client, 0)
                for ln in child_md.splitlines():
                    lines.append(f"    {ln}\n")

    elif btype == "toggle":
        text = rich_text_to_md(data.get("rich_text", []))
        lines.append(f'??? note "{text}"\n')
        if block.get("has_children"):
            for child in get_all_blocks(client, block["id"]):
                child_md = block_to_md(child, client, 0)
                for ln in child_md.splitlines():
                    lines.append(f"    {ln}\n")
        lines.append("\n")

    elif btype == "divider":
        lines.append("\n---\n")

    elif btype == "image":
        url = (data.get("external") or data.get("file") or {}).get("url", "")
        caption = rich_text_to_md(data.get("caption", []))
        lines.append(f"![{caption or 'image'}]({url})\n")
        if caption:
            lines.append(f"*{caption}*\n")

    elif btype == "to_do":
        text = rich_text_to_md(data.get("rich_text", []))
        checked = "x" if data.get("checked") else " "
        lines.append(f"{indent}- [{checked}] {text}\n")

    elif btype == "table":
        # Fetch rows and render as markdown table
        rows = get_all_blocks(client, block["id"])
        for i, row in enumerate(rows):
            cells = row.get("table_row", {}).get("cells", [])
            row_md = " | ".join(rich_text_to_md(cell) for cell in cells)
            lines.append(f"| {row_md} |\n")
            if i == 0:
                separator = " | ".join("---" for _ in cells)
                lines.append(f"| {separator} |\n")
        lines.append("\n")

    elif btype == "table_row":
        pass  # handled inside "table" above

    elif btype == "equation":
        expr = data.get("expression", "")
        lines.append(f"$${expr}$$\n")

    elif btype == "bookmark":
        url = data.get("url", "")
        caption = rich_text_to_md(data.get("caption", [])) or url
        lines.append(f"🔗 [{caption}]({url})\n")

    elif btype == "link_preview":
        url = data.get("url", "")
        lines.append(f"🔗 [{url}]({url})\n")

    # Generic children fallback (not for types already handling children above)
    if block.get("has_children") and btype not in (
        "table", "child_page", "child_database",
        "bulleted_list_item", "numbered_list_item", "callout", "toggle",
    ):
        for child in get_all_blocks(client, block["id"]):
            lines.append(block_to_md(child, client, depth + 1))

    return "".join(lines)


def get_page_title(page: dict) -> str:
    props = page.get("properties", {})
    for key in ("Name", "Title", "title", "name"):
        if key in props:
            prop = props[key]
            if prop.get("type") == "title":
                title = rich_text_to_md(prop.get("title", []))
                if title:
                    return title
    if page.get("object") == "block" and page.get("type") == "child_page":
        return page.get("child_page", {}).get("title", "untitled")
    return "untitled"


def sync_page(client: Client, page_id: str, output_dir: Path, synced: list, indent: str = "", is_root: bool = False):
    output_dir.mkdir(parents=True, exist_ok=True)

    page = client.pages.retrieve(page_id=page_id)
    if page.get("object") != "page":
        return

    title = get_page_title(page)
    blocks = get_all_blocks(client, page_id)

    if not is_root:
        # Convert blocks to markdown lines first so we can scan for tag: / tags:
        body_lines = []
        for block in blocks:
            body_lines.append(block_to_md(block, client))

        # Scan rendered lines for a "tags: X, Y" or "tag: X" pattern and strip it
        import re as _re
        tags = []
        filtered = []
        for ln in body_lines:
            m = _re.match(r'^tags?:\s*(.+)', ln.strip(), _re.IGNORECASE)
            if m:
                tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
            else:
                filtered.append(ln)

        front_matter = ""
        if tags:
            tag_lines = "\n".join(f"  - {t}" for t in tags)
            front_matter = f"---\ntags:\n{tag_lines}\n---\n\n"

        lines = [front_matter, f"# {title}\n\n"] + filtered

        filename = slugify(title) + ".md"
        filepath = output_dir / filename
        filepath.write_text("".join(lines), encoding="utf-8")
        rel = filepath.relative_to(Path(__file__).parent / "docs").as_posix()
        print(f"{indent}+ {title}  →  docs/{rel}")
        synced.append((title, rel))
    else:
        print(f"[root] {title}  →  skipped (container page)")

    child_pages = [b for b in blocks if b.get("type") == "child_page"]
    if child_pages:
        child_dir = output_dir / slugify(title) if not is_root else output_dir
        for child in child_pages:
            sync_page(client, child["id"], child_dir, synced, indent + "  ")


def build_nav_tree(synced: list) -> list:
    """Build nav tree mirroring Notion hierarchy.

    - Root page and its direct children are flat at the top level.
    - Pages that have sub-pages become collapsible sections.
    """
    from pathlib import PurePosixPath

    by_parent: dict = {}
    for title, rel_path in synced:
        parent = str(PurePosixPath(rel_path).parent)
        by_parent.setdefault(parent, []).append((title, rel_path))

    has_children = set()
    for title, rel_path in synced:
        page_dir = str(PurePosixPath(rel_path).with_suffix(""))
        if page_dir in by_parent:
            has_children.add(rel_path)

    def make_items(parent_dir: str) -> list:
        items = []
        for title, rel_path in by_parent.get(parent_dir, []):
            page_dir = str(PurePosixPath(rel_path).with_suffix(""))
            if rel_path in has_children:
                sub = [{title: rel_path}] + make_items(page_dir)
                items.append({title: sub})
            else:
                items.append({title: rel_path})
        return items

    # Root container is never in synced; top-level pages land directly at notion/
    return make_items("notion")


def nav_to_yaml_lines(items: list, indent: int) -> list:
    lines = []
    pad = " " * indent
    for item in items:
        for key, val in item.items():
            if isinstance(val, str):
                lines.append(f"{pad}- {key}: {val}")
            else:
                lines.append(f"{pad}- {key}:")
                lines.extend(nav_to_yaml_lines(val, indent + 4))
    return lines


def update_mkdocs_nav(synced: list, mkdocs_path: Path):
    nav_tree = build_nav_tree(synced)
    nav_lines = ["  - Notion:"] + nav_to_yaml_lines(nav_tree, indent=6)

    file_lines = mkdocs_path.read_text().splitlines()

    # Find the Notion section start and end
    start = end = None
    for i, line in enumerate(file_lines):
        if start is None and line.rstrip() == "  - Notion:":
            start = i
        elif start is not None:
            stripped = line.strip()
            indent_len = len(line) - len(line.lstrip()) if stripped else 999
            # Stop at next same-level nav item or a non-indented line (plugins:, etc.)
            if stripped and (
                (stripped.startswith("- ") and indent_len <= 2)
                or not line.startswith(" ")
            ):
                end = i
                break

    if start is None:
        # No Notion section yet — insert before plugins:
        result = []
        for line in file_lines:
            if line.startswith("plugins:"):
                result.extend(nav_lines)
                result.append("")
            result.append(line)
        mkdocs_path.write_text("\n".join(result))
    else:
        if end is None:
            end = len(file_lines)
        # Preserve blank line that was before the next section
        blank = [""] if end > 0 and file_lines[end - 1].strip() == "" else []
        new_lines = file_lines[:start] + nav_lines + blank + file_lines[end:]
        mkdocs_path.write_text("\n".join(new_lines))

    print(f"mkdocs.yml  →  Notion section updated ({len(synced)} pages)")


def generate_home_page(synced: list, docs_dir: Path):
    """Auto-generate index.md with quick-link cards for every synced page."""
    cards = []
    icons = {
        "kafka": "🟠", "kubernetes": "☸️", "k8s": "☸️", "kk8s": "☸️",
        "test": "🧪", "notes": "📒", "archive": "🗄️",
    }

    def pick_icon(title: str) -> str:
        low = title.lower()
        for key, icon in icons.items():
            if key in low:
                return icon
        return "📄"

    for title, rel_path in synced:
        icon = pick_icon(title)
        cards.append(
            f"-   {icon} **[{title}]({rel_path})**\n\n"
            f"    Quick access to {title} notes."
        )

    cards_block = "\n\n".join(cards)

    content = f"""# MuzOps Learning Zone

> Personal learning notes on Kubernetes, DevOps, Kafka, and Cloud Engineering.

---

## Quick Links

<div class="grid cards" markdown>

{cards_block}

</div>

---

## Recently Read

<div id="recent-pages">
  <em>Loading recently visited pages...</em>
</div>
"""

    home = docs_dir.parent / "index.md"
    home.write_text(content, encoding="utf-8")
    print(f"index.md    →  home page regenerated ({len(synced)} quick links)")


def main():
    if not NOTION_TOKEN:
        print("ERROR: Set NOTION_TOKEN environment variable.")
        sys.exit(1)
    if not NOTION_PAGE_ID:
        print("ERROR: Set NOTION_PAGE_ID environment variable.")
        sys.exit(1)

    client = Client(auth=NOTION_TOKEN)
    synced = []
    sync_page(client, NOTION_PAGE_ID, DOCS_DIR, synced, is_root=True)

    # Remove .md files that no longer exist in Notion.
    # Collect into a list first — deleting dirs mid-rglob causes FileNotFoundError.
    synced_paths = {Path(__file__).parent / "docs" / rel for _, rel in synced}
    orphans = [p for p in list(DOCS_DIR.rglob("*.md")) if p not in synced_paths]
    for existing in orphans:
        if not existing.exists():
            continue
        existing.unlink()
        print(f"  - removed: docs/{existing.relative_to(Path(__file__).parent / 'docs').as_posix()}")
        for parent in existing.parents:
            if parent == DOCS_DIR:
                break
            if parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()

    update_mkdocs_nav(synced, MKDOCS_YML)
    generate_home_page(synced, DOCS_DIR)
    print(f"\nDone. {len(synced)} page(s) synced.")


if __name__ == "__main__":
    main()
