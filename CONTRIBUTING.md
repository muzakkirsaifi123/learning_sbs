# Contributing

This repo is two different things, and they take contributions differently.

## The content (`docs/notion/`)

Everything under `docs/notion/` is generated from a private Notion workspace by `notion_sync.py` and gets overwritten on the next scheduled sync (every 3 hours) — **a pull request editing these files directly will be silently reverted.** If you spot an error, a broken link, or want to suggest a topic, open an issue using the "Content suggestion" template instead. It becomes a note the maintainer adds to Notion.

The one exception is [`docs/kubernetes_operators/kubernetes_operator.md`](docs/kubernetes_operators/kubernetes_operator.md) — that page is hand-written and lives directly in the repo, so normal PRs against it are fine.

## The pipeline (everything else)

`notion_sync.py`, `mkdocs.yml`, the GitHub Actions workflows, `scripts/`, `snippets/`, `overrides/`, and the site chrome under `docs/assets/` are regular code — PRs welcome.

Before opening one:

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v          # sync-engine and doc-quality-check tests
mkdocs build --strict                # what CI runs before it'll deploy
python3 scripts/check_docs.py        # broken links / front matter / orphan pages
```

If you're changing `notion_sync.py`, add or update a test in `tests/test_notion_sync.py` — it runs against a mocked Notion client, so it doesn't need real credentials. See the module docstring for what it currently proves (idempotency, rename/delete handling, image cleanup).

## Reporting a security issue

If you find something like the `properdocs` supply-chain issue documented in this repo's git history, please open an issue rather than a PR so it gets visibility before anyone merges around it.
