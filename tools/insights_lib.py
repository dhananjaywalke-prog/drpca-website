"""Shared helpers for the drpca.com Insights section.

Used by new_insight.py (publish one article) and rebuild_feeds.py
(regenerate sitemap.xml and rss.xml from insights/articles.json).
No third-party dependencies beyond `markdown` and `jinja2`, both
available in a standard Python install used with Claude Code.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSIGHTS = ROOT / "insights"
ARTICLES_JSON = INSIGHTS / "articles.json"
SITEMAP = ROOT / "sitemap.xml"
RSS = ROOT / "rss.xml"
TEMPLATE = ROOT / "tools" / "article_template.html"

SITE = "https://drpca.com"
SITE_NAME = "DRP & Co. LLP"
LOGO = f"{SITE}/assets/drpca-logo.png"

# Static pages that belong in the sitemap besides the articles.
STATIC_PAGES = [
    ("", "1.0", "weekly"),
    ("about", "0.8", "monthly"),
    ("services", "0.8", "monthly"),
    ("services/audit-assurance", "0.7", "monthly"),
    ("services/tax-advisory", "0.7", "monthly"),
    ("services/governance", "0.7", "monthly"),
    ("services/valuation", "0.7", "monthly"),
    ("services/financial-advisory", "0.7", "monthly"),
    ("services/techno-economic", "0.7", "monthly"),
    ("services/wealth-management", "0.7", "monthly"),
    ("insights", "0.9", "weekly"),
    ("contact", "0.6", "monthly"),
    ("careers", "0.6", "monthly"),
    ("privacy", "0.3", "yearly"),
    ("terms", "0.3", "yearly"),
]

CATEGORIES = {
    # category label -> stripe class used by the listing page CSS
    "Valuation": "valuation",
    "Regulatory": "regulatory",
    "Tax": "tax",
    "Governance": "governance",
    "General": "general",
}

AUTHORS = {
    "Dhananjay Walke": {
        "name": "CA Dhananjay Walke",
        "role": "Managing Partner, DRP &amp; Co. LLP",
        "avatar": "/assets/team/dhananjay-walke.jpg",
        "linkedin": "https://www.linkedin.com/in/dhananjaywalke/",
    },
    "Rohan Adkar": {
        "name": "CA Rohan Adkar",
        "role": "Partner, DRP &amp; Co. LLP",
        "avatar": "/assets/team/rohan-adkar.jpg",
        "linkedin": "",
    },
    "Priyank Vaidya": {
        "name": "CA Priyank Vaidya",
        "role": "Partner, DRP &amp; Co. LLP",
        "avatar": "/assets/team/priyank-vaidya.jpg",
        "linkedin": "https://www.linkedin.com/in/fca-priyank-vaidya-02a09a18/",
    },
}

# Sidebar call-to-action per category. Factual, no solicitation beyond
# the site's existing "Get in Touch" wording (ICAI Code of Ethics).
CTA = {
    "Governance": ("Corporate Governance", "The firm advises boards and promoters on governance, due diligence and compliance matters.", "/services/governance"),
    "Valuation": ("Business Valuation", "The firm carries out valuations under Rule 11UA, the Companies Act and IBBI standards.", "/services/valuation"),
    "Regulatory": ("Regulatory Advisory", "The firm assists with SEBI, RBI and Companies Act compliance matters.", "/services/governance"),
    "Tax": ("Tax Advisory", "The firm's tax practice covers corporate taxation, GST, transfer pricing and international tax.", "/services/tax-advisory"),
    "General": ("Have a question?", "Reach out to discuss any topic covered in the firm's articles.", "/contact"),
}

STANDARD_DISCLAIMER = (
    "<strong>Disclaimer:</strong> This article is prepared for general information purposes and "
    "should not be construed as professional advice. Views expressed are those of the author. "
    "Readers are advised to consult a qualified professional before acting on anything in this "
    "article. DRP &amp; Co. LLP does not accept any liability for actions taken based on this article."
)

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⭐⭕️‍❤✔✅❌⬆⬇]"
)


# ---------- small utilities ----------

def strip_emoji(text: str) -> str:
    text = EMOJI_RE.sub("", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def fix_double_encoding(text: str) -> str:
    return text.replace("&amp;amp;", "&amp;").replace("&amp;quot;", "&quot;").replace("&amp;#39;", "&#39;")


def rupee(text: str) -> str:
    """House style: Rs. rather than the ₹ sign."""
    return re.sub(r"₹\s*", "Rs. ", text)


def no_em_dashes(text: str) -> str:
    # House style: no em-dashes. Replace with a comma-space or a full stop depending on context.
    text = text.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ")
    return text


def slugify(title: str, max_words: int = 9) -> str:
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    words = [w for w in re.split(r"[\s-]+", s) if w]
    return "-".join(words[:max_words])


def reading_time(text: str) -> int:
    words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", text)))
    return max(1, round(words / 200))


def date_display(d: date) -> str:
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# ---------- articles.json ----------

def load_articles() -> list[dict]:
    return json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))


def save_articles(articles: list[dict]) -> None:
    articles.sort(key=lambda a: a["date"], reverse=True)
    ARTICLES_JSON.write_text(json.dumps(articles, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------- structured data ----------

def article_jsonld(a: dict, author_key: str, description: str, modified: str | None = None) -> str:
    author = AUTHORS[author_key]
    url = f"{SITE}/insights/{a['slug']}/"
    data = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": a["title"],
            "description": description,
            "url": url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "datePublished": a["date"],
            "dateModified": modified or a["date"],
            "author": {
                "@type": "Person",
                "name": html.unescape(author["name"]),
                "jobTitle": html.unescape(author["role"]).split(",")[0],
                "worksFor": {"@type": "Organization", "name": SITE_NAME},
                **({"url": author["linkedin"]} if author["linkedin"] else {}),
            },
            "publisher": {
                "@type": "Organization",
                "name": SITE_NAME,
                "url": SITE,
                "logo": {"@type": "ImageObject", "url": LOGO},
            },
            "image": a.get("image") or LOGO,
            "articleSection": a["category"],
            "inLanguage": "en-IN",
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{SITE}/insights/"},
                {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
            ],
        },
    ]
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


# ---------- feeds ----------

def write_sitemap(articles: list[dict]) -> None:
    today = date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio, freq in STATIC_PAGES:
        loc = f"{SITE}/{path}" if path else f"{SITE}/"
        out.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>")
    for a in articles:
        out.append(f"  <url><loc>{SITE}/insights/{a['slug']}/</loc><lastmod>{a.get('modified', a['date'])}</lastmod><changefreq>yearly</changefreq><priority>0.6</priority></url>")
    out.append("</urlset>")
    SITEMAP.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_rss(articles: list[dict], limit: int = 25) -> None:
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for a in articles[:limit]:
        pub = datetime.strptime(a["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 06:00:00 +0530")
        link = f"{SITE}/insights/{a['slug']}/"
        author = AUTHORS.get(a.get("author", "Dhananjay Walke"), AUTHORS["Dhananjay Walke"])
        items.append(
            "    <item>\n"
            f"      <title>{esc(a['title'])}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <category>{esc(a['category'])}</category>\n"
            f"      <dc:creator>{esc(html.unescape(author['name']))}</dc:creator>\n"
            f"      <description>{esc(a['summary'])}</description>\n"
            "    </item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        "  <channel>\n"
        f"    <title>{esc(SITE_NAME)} Insights</title>\n"
        f"    <link>{SITE}/insights/</link>\n"
        f'    <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>\n'
        "    <description>Articles on valuation, governance, regulatory and tax matters from DRP &amp; Co. LLP, Chartered Accountants, Pune.</description>\n"
        "    <language>en-in</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items) + "\n"
        "  </channel>\n"
        "</rss>\n"
    )
    RSS.write_text(xml, encoding="utf-8")


def rebuild_feeds() -> None:
    articles = load_articles()
    write_sitemap(articles)
    write_rss(articles)
