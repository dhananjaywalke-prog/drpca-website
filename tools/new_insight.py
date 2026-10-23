#!/usr/bin/env python3
"""Generate one Insights article page from a Markdown source file.

Usage:
    python3 tools/new_insight.py tools/src/<slug>.md            # build (or rebuild) the article
    python3 tools/new_insight.py tools/src/<slug>.md --dry-run  # print what would change, write nothing

Source file format (YAML-style front matter, then Markdown body):

    ---
    title: When a relative's business ends an independent director's term
    hook: Her son's petrol pump ended her board seat.
    category: Governance            # Valuation | Regulatory | Tax | Governance | General
    date: 2026-10-14                # LinkedIn posting date
    author: Dhananjay Walke         # key in insights_lib.AUTHORS (default: Dhananjay Walke)
    linkedin_url: https://www.linkedin.com/feed/update/urn:li:activity:7515977195002040320/
    news_based: true                # adds "Written on <date>, based on public reports at that time."
    summary: One or two sentences for the listing card and meta description.
    closing_question: What would your board have done?
    slug: sebi-independent-director-relative-transactions   # optional, derived from title if absent
    ---
    Post text in Markdown. Blank line between paragraphs. Use "## Heading" only where
    the post naturally breaks into sections.

    ## Background
    Everything under this heading is rendered in the boxed Background section.
    Cite the primary source: "Source: SEBI (LODR) Regulations, 2015, Reg. 16(1)(b)
    [link](https://www.sebi.gov.in/...)".

What the script does:
  1. Converts Markdown to HTML, strips emojis and em-dashes, builds a table of contents from H2s.
  2. Picks three related articles (same category first, most recent).
  3. Renders tools/article_template.html to insights/<slug>/index.html.
  4. Adds or updates the entry in insights/articles.json.
  5. Regenerates sitemap.xml and rss.xml.
It never commits or pushes. That is done by the person reviewing the preview.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insights_lib as lib  # noqa: E402


def parse_source(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{path}: missing front matter block (--- ... ---)")
    meta: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.split(" #", 1)[0].strip().strip('"').strip("'")
        meta[k.strip()] = v
    return meta, m.group(2).strip()


def split_background(body_md: str) -> tuple[str, str]:
    parts = re.split(r"^##\s+Background\s*$", body_md, maxsplit=1, flags=re.M | re.I)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return body_md, ""


def md_to_html(md: str) -> str:
    md = lib.rupee(lib.no_em_dashes(lib.strip_emoji(md)))
    out = markdown.markdown(md, extensions=["sane_lists", "smarty"], output_format="html5")
    # Give every H2 an id for the TOC
    counter = [0]

    def add_id(m):
        counter[0] += 1
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = "section-" + lib.slugify(text, 6)
        return f'<h2 id="{sid}">{m.group(1)}</h2>'

    out = re.sub(r"<h2>(.*?)</h2>", add_id, out)
    # Indent to match the hand-written pages
    return "\n".join("        " + line if line.strip() else "" for line in out.splitlines())


def toc_from_html(body_html: str) -> list[dict]:
    return [{"id": i, "text": re.sub(r"<[^>]+>", "", t)}
            for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)]


def pick_related(articles: list[dict], slug: str, category: str, n: int = 3) -> list[dict]:
    others = [a for a in articles if a["slug"] != slug]
    same = [a for a in others if a["category"] == category]
    rest = [a for a in others if a["category"] != category]
    return (same + rest)[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = Path(args.source)
    meta, body_md = parse_source(src)

    required = ["title", "category", "date", "summary"]
    missing = [k for k in required if not meta.get(k)]
    if missing:
        sys.exit(f"{src}: missing required fields: {', '.join(missing)}")
    if meta["category"] not in lib.CATEGORIES:
        sys.exit(f"{src}: category must be one of {', '.join(lib.CATEGORIES)}")

    author_key = meta.get("author", "Dhananjay Walke")
    if author_key not in lib.AUTHORS:
        sys.exit(f"{src}: unknown author '{author_key}'. Add them to tools/insights_lib.py AUTHORS first.")
    author = dict(lib.AUTHORS[author_key])
    author["initials"] = "".join(w[0] for w in re.sub(r"<[^>]+>", "", author["name"]).replace("CA ", "").split()[:2])

    slug = meta.get("slug") or lib.slugify(meta["title"])
    pub = date.fromisoformat(meta["date"])
    title = lib.rupee(lib.no_em_dashes(lib.strip_emoji(meta["title"])))
    summary = lib.rupee(lib.no_em_dashes(lib.strip_emoji(meta["summary"])))
    hook = lib.no_em_dashes(lib.strip_emoji(meta.get("hook", "")))

    post_md, background_md = split_background(body_md)
    body_html = md_to_html(post_md)
    background_html = md_to_html(background_md) if background_md else ""
    background_html = background_html.replace("<p>Source:", '<p class="source">Source:')
    toc = toc_from_html(body_html)
    if background_html:
        toc.append({"id": "section-background", "text": "Background"})

    full_text = hook + " " + body_html + " " + background_html
    rt = lib.reading_time(full_text)

    articles = lib.load_articles()
    entry = {
        "slug": slug,
        "title": title,
        "date": pub.isoformat(),
        "date_display": lib.date_display(pub),
        "category": meta["category"],
        "cat_stripe": lib.CATEGORIES[meta["category"]],
        "reading_time": rt,
        "summary": summary,
        "author": author_key,
    }
    if hook:
        entry["hook"] = hook
    if meta.get("linkedin_url"):
        entry["linkedin_url"] = meta["linkedin_url"]

    as_of = ""
    if meta.get("news_based", "").lower() in ("true", "yes", "1"):
        as_of = f"Written on {pub.strftime('%d %B %Y')}, based on public reports at that time."

    cta_h, cta_t, cta_l = lib.CTA[meta["category"]]

    env = Environment(loader=FileSystemLoader(str(lib.TEMPLATE.parent)), autoescape=select_autoescape(["html"]))
    page = env.get_template(lib.TEMPLATE.name).render(
        title=title,
        summary=summary,
        url=f"{lib.SITE}/insights/{slug}/",
        image=lib.LOGO,
        date_iso=pub.isoformat(),
        date_display=entry["date_display"],
        category=meta["category"],
        reading_time=rt,
        author=author,
        hook=hook,
        as_of=as_of,
        body=body_html,
        background=background_html,
        linkedin_url=meta.get("linkedin_url", ""),
        closing_question=meta.get("closing_question", ""),
        disclaimer=lib.STANDARD_DISCLAIMER,
        toc=toc,
        related=pick_related(articles, slug, meta["category"]),
        cta={"heading": cta_h, "text": cta_t, "link": cta_l},
        jsonld=lib.article_jsonld(entry, author_key, summary),
    )

    out_dir = lib.INSIGHTS / slug
    existing = [a for a in articles if a["slug"] == slug]
    action = "update" if existing else "create"

    if args.dry_run:
        print(f"[dry-run] would {action} insights/{slug}/index.html ({rt} min read, {len(toc)} TOC entries)")
        print(f"[dry-run] articles.json entry: {entry}")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    articles = [a for a in articles if a["slug"] != slug] + [entry]
    lib.save_articles(articles)
    lib.rebuild_feeds()
    print(f"{action}d insights/{slug}/index.html")
    print(f"updated insights/articles.json, sitemap.xml, rss.xml")
    print(f"preview path: /insights/{slug}/")


if __name__ == "__main__":
    main()
