import importlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


class CheckDocsTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="check-docs-test-"))
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)
        (self.tmpdir / "docs" / "notion").mkdir(parents=True)
        (self.tmpdir / "mkdocs.yml").write_text("nav:\n  - Home: index.md\n")

        import check_docs
        importlib.reload(check_docs)
        self.mod = check_docs
        self.mod.ROOT = self.tmpdir
        self.mod.DOCS_DIR = self.tmpdir / "docs"
        self.mod.MKDOCS_YML = self.tmpdir / "mkdocs.yml"

    def write(self, rel, content):
        p = self.mod.DOCS_DIR / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return p

    def test_valid_relative_link_passes(self):
        self.write("notion/a.md", "# A\n\n[link to b](b.md)\n")
        self.write("notion/b.md", "# B\n\ncontent\n")
        errors = self.mod.check_links(self.mod.iter_markdown_files())
        self.assertEqual(errors, [])

    def test_broken_relative_link_is_caught(self):
        self.write("notion/a.md", "# A\n\n[dead link](does-not-exist.md)\n")
        errors = self.mod.check_links(self.mod.iter_markdown_files())
        self.assertEqual(len(errors), 1)
        self.assertIn("does-not-exist.md", errors[0])

    def test_external_and_anchor_links_are_ignored(self):
        self.write("notion/a.md", "# A\n\n[ext](https://example.com)\n[anchor](#section)\n")
        errors = self.mod.check_links(self.mod.iter_markdown_files())
        self.assertEqual(errors, [])

    def test_empty_page_detected(self):
        self.write("notion/empty.md", "# Empty\n\n")
        self.write("notion/full.md", "# Full\n\nSome real content here.\n")
        empty = self.mod.check_empty_pages(self.mod.iter_markdown_files())
        rels = [Path(e).name for e in empty]
        self.assertIn("empty.md", rels)
        self.assertNotIn("full.md", rels)

    def test_snippet_include_alone_does_not_count_as_content(self):
        self.write("notion/empty.md", '# Empty\n\n--8<-- "abbreviations.md"\n')
        empty = self.mod.check_empty_pages(self.mod.iter_markdown_files())
        self.assertEqual(len(empty), 1)

    def test_orphan_page_detected(self):
        (self.mod.MKDOCS_YML).write_text("nav:\n  - Notion:\n      - A: notion/a.md\n")
        self.write("notion/a.md", "# A\n\ncontent\n")
        self.write("notion/orphan.md", "# Orphan\n\ncontent\n")
        orphans = self.mod.check_orphans(self.mod.iter_markdown_files())
        self.assertEqual(orphans, ["notion/orphan.md"])

    def test_invalid_front_matter_detected(self):
        self.write("notion/bad.md", "---\ntags: [unterminated\n---\n\n# Bad\n\ncontent\n")
        errors = self.mod.check_front_matter(self.mod.iter_markdown_files())
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
