#!/usr/bin/env python3
"""One-off clean-up of the 36 legacy Insights pages (Oct 2026). Safe to re-run.

- strips emojis from titles, bodies, meta descriptions and articles.json
- fixes &amp;amp; double encoding
- rewrites canonical / og:url from www.drpca.com to drpca.com
- adds Article + BreadcrumbList JSON-LD and an RSS <link> where missing
- removes related-article links that point to pages that don't exist
- adds an `author` field to every articles.json entry
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insights_lib as lib  # noqa: E402

# Articles not written by DW
AUTHOR_OVERRIDES = {"new-tax-regime-ay-2026-27": "Rohan Adkar"}


def clean_page(a: dict) -> list[str]:
    path = lib.INSIGHTS / a["slug"] / "index.html"
    if not path.exists():
        return [f"MISSING page for {a['slug']}"]
    html = path.read_text(encoding="utf-8")
    orig = html
    notes = []

    # 1. encoding + emoji (emoji only outside <style>/<script>, which have none anyway)
    html = lib.fix_double_encoding(html)
    head, sep, body = html.partition("<body")
    n = len(lib.EMOJI_RE.findall(html))
    if n:
        html = lib.EMOJI_RE.sub("", html)
        html = re.sub(r"<p>\s*</p>", "", html)
        notes.append(f"removed {n} emoji")

    # 2. host
    if "www.drpca.com" in html:
        html = html.replace("https://www.drpca.com", lib.SITE)
        notes.append("canonical -> drpca.com")
    # canonical with trailing slash to match the served URL
    html = re.sub(r'(rel="canonical" href="%s/insights/[^"/]+)"' % re.escape(lib.SITE), r'\1/"', html)
    html = re.sub(r'(property="og:url" content="%s/insights/[^"/]+)"' % re.escape(lib.SITE), r'\1/"', html)

    # 3. broken related links
    def check_link(m):
        slug = m.group(1)
        return m.group(0) if (lib.INSIGHTS / slug).is_dir() else ""
    before = html
    html = re.sub(r'<a href="/insights/([a-z0-9-]+)/?" class="related-card">.*?</a>\s*', check_link, html, flags=re.S)
    if html != before:
        notes.append("removed broken related links")
        # drop an emptied related block
        html = re.sub(r'<!-- Related Articles -->\s*<div class="sidebar-block">\s*<div class="sidebar-label">Related Articles</div>\s*</div>\s*', "", html)

    # 4. structured data + rss link
    if "application/ld+json" not in html:
        desc = re.search(r'<meta name="description" content="([^"]*)"', html)
        description = lib.fix_double_encoding(desc.group(1)) if desc else a["summary"]
        import html as h
        jsonld = lib.article_jsonld(a, a.get("author", "Dhananjay Walke"), h.unescape(description))
        html = html.replace("</head>", "    " + jsonld + "\n</head>", 1)
        notes.append("added JSON-LD")
    if 'type="application/rss+xml"' not in html:
        html = html.replace('<link rel="icon" type="image/svg+xml" href="/favicon.svg">',
                            '<link rel="icon" type="image/svg+xml" href="/favicon.svg">\n    <link rel="alternate" type="application/rss+xml" title="DRP &amp; Co. LLP Insights" href="/rss.xml">', 1)

    if html != orig:
        path.write_text(html, encoding="utf-8")
    return notes


def main():
    articles = lib.load_articles()
    for a in articles:
        a["title"] = lib.strip_emoji(a["title"])
        a["summary"] = lib.fix_double_encoding(lib.strip_emoji(a["summary"]))
        a.setdefault("author", AUTHOR_OVERRIDES.get(a["slug"], "Dhananjay Walke"))
        notes = clean_page(a)
        if notes:
            print(f"{a['slug'][:48]:48} {', '.join(notes)}")
    lib.save_articles(articles)
    lib.rebuild_feeds()
    print("articles.json, sitemap.xml, rss.xml rewritten")


if __name__ == "__main__":
    main()
