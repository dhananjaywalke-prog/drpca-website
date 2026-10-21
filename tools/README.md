# Insights toolkit

| File | Purpose |
|---|---|
| `new_insight.py` | Build one article page from `tools/src/<slug>.md`; updates articles.json, sitemap.xml, rss.xml |
| `rebuild_feeds.py` | Regenerate sitemap.xml and rss.xml after hand edits to articles.json |
| `clean_legacy.py` | One-off clean-up run in Oct 2026 (emoji, encoding, canonical host, JSON-LD). Safe to re-run |
| `insights_lib.py` | Shared constants: authors, categories, CTA text, disclaimer, feed writers |
| `article_template.html` | Jinja template; CSS, nav and footer copied from the site's article layout |

Workflow: `/new-insight` in Claude Code, or by hand:

    python3 tools/new_insight.py tools/src/<slug>.md
    git checkout -b insight/<slug> && git add -A && git commit && git push -u origin insight/<slug>
    gh pr create

Never push to `main` directly. The PR's Netlify deploy preview is the review step; merging publishes.
Requires Python 3.9+ with `markdown` and `jinja2` (`pip install markdown jinja2`).
