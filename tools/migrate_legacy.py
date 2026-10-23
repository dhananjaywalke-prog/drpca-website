#!/usr/bin/env python3
"""One-off (Oct 2026): rebuild the 35 legacy LinkedIn-export articles through the
current template. Extracts each page's <article class="article-body"> HTML, converts
it to Markdown, writes tools/src/<slug>.md with the original LinkedIn article URL,
then runs new_insight.py on it. Safe to re-run; skips slugs whose source already exists
unless --force is given.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from markdownify import markdownify as md

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insights_lib as lib  # noqa: E402

# site slug -> LinkedIn article (pulse) slug, read from DW's Articles page on 23 Oct 2026
PULSE = {
 "where-does-your-tax-money-go-past-6-budgets-272-lakh-crores": "where-does-your-tax-money-go-past-6-budgets-272-lakh-crores-walke-1i30f",
 "sme-ipo-boom-10-rbi-insights-every-professional-should": "sme-ipo-boom-10-rbi-insights-every-professional-should-walke-vpmmc",
 "capm-vs-build-up-two-roads-finding-true-cost-equity": "capm-vs-build-up-two-roads-finding-true-cost-equity-dhananjay-walke-3fr6f",
 "decoding-build-up-method-finding-true-cost-equity-india": "decoding-build-up-method-finding-true-cost-equity-india-walke-ckhcf",
 "section-247-law-brought-evolved-business-valuation-india": "section-247-law-brought-evolved-business-valuation-india-walke-hwjcf",
 "sebis-reit-reclassification-new-era-indian-real-estate": "sebis-reit-reclassification-new-era-indian-real-estate-walke-qq6zf",
 "rbis-revised-prudential-norms-ucbs-game-changer-challenge": "rbis-revised-prudential-norms-ucbs-game-changer-challenge-walke-nfcxf",
 "valuation-conclusions-case-inconsistent-results-across": "valuation-conclusions-case-inconsistent-results-across-walke-6b9mf",
 "engine-democracy-how-indian-parliament-truly-functions": "engine-democracy-how-indian-parliament-truly-functions-walke-34ksf",
 "adapting-change-sebis-new-sme-framework-its-impact-ipo": "adapting-change-sebis-new-sme-framework-its-impact-ipo-walke-vippf",
 "unlocking-tax-savings-how-unpaid-expenses-impact-your": "unlocking-tax-savings-how-unpaid-expenses-impact-your-dhananjay-walke-kthwf",
 "navigating-ibc-terrain-insights-from-rbi-governors-speech": "navigating-ibc-terrain-insights-from-rbi-governors-speech-walke-rl0mf",
 "rbis-new-guidelines-commercial-papers-non-convertible": "rbis-new-guidelines-commercial-papers-non-convertible-dhananjay-walke-3gd5f",
 "orderly-vs-forced-liquidation-value": "orderly-vs-forced-liquidation-value-dhananjay-walke",
 "discount-rates-vs-capitalization": "discount-rates-vs-capitalization-dhananjay-walke",
 "navigating-startup-business-valuation": "navigating-startup-business-valuation-dhananjay-walke",
 "dloc-vs-dlom": "dloc-vs-dlom-dhananjay-walke",
 "terminal-growth-rate-business-valuation": "terminal-growth-rate-business-valuation-dhananjay-walke",
 "estimating-terminal-value": "estimating-terminal-value-dhananjay-walke",
 "intrinsic-value-vs-investment": "intrinsic-value-vs-investment-dhananjay-walke",
 "fcff-vs-fcfe": "fcff-vs-fcfe-dhananjay-walke",
 "how-comparable-guideline-private-transactions": "how-comparable-guideline-private-transactions-dhananjay-walke",
 "concept-degree-marketability-business-valuation": "concept-degree-marketability-business-valuation-dhananjay-walke",
 "valuation-date-business-valuations": "valuation-date-business-valuations-dhananjay-walke",
 "you-valuing-securities-assets": "you-valuing-securities-assets-dhananjay-walke",
 "principles-valuation-appraisal": "principles-valuation-appraisal-dhananjay-walke",
 "standard-value-premise-business-valuation": "standard-value-premise-business-valuation-dhananjay-walke",
 "impact-rising-interest-rates-business-valuation": "impact-rising-interest-rates-business-valuation-dhananjay-walke",
 "importance-financial-statement-analysis-process-business": "importance-financial-statement-analysis-process-business-walke",
 "purpose-valuation-its-impact-exercise": "purpose-valuation-its-impact-exercise-dhananjay-walke",
 "valuation-adjustments-fair-value-measurement": "valuation-adjustments-fair-value-measurement-dhananjay-walke",
 "fair-value-hierarchy": "fair-value-hierarchy-dhananjay-walke",
 "understanding-fair-value-part-2": "understanding-fair-value-part-2-dhananjay-walke",
 "understanding-fair-value-part-1": "understanding-fair-value-part-1-dhananjay-walke",
 "how-use-lockdown-time-recovery-post-corona-crisis": "how-use-lockdown-time-recovery-post-corona-crisis-dhananjay-walke",
}


def body_html(page: str) -> str:
    m = re.search(r'<article class="article-body">(.*?)</article>', page, re.S)
    if not m:
        raise SystemExit("no article-body found")
    return m.group(1)


def to_markdown(html: str) -> str:
    html = html.replace("⃣", "")                      # keycap combiner left behind by emoji strip
    html = re.sub(r"<h3>", "<h2>", html); html = re.sub(r"</h3>", "</h2>", html)
    html = re.sub(r"<hr\s*/?>", "", html)
    # move padding out of inline tags so markdown markers hug the words
    html = re.sub(r"<(strong|em|b|i)>(\s|&nbsp;)+", r" <\1>", html)
    html = re.sub(r"(\s|&nbsp;)+</(strong|em|b|i)>", r"</\2> ", html)
    html = re.sub(r"<(strong|em)>\s*</\1>", "", html)
    html = re.sub(r'<ul class="article-list">', "<ul>", html)
    html = re.sub(r'<ol class="article-list">', "<ol>", html)
    text = md(html, heading_style="ATX", bullets="-", strip=["div", "span"])
    text = text.replace(" ", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # markdownify wraps <li><p> as "- \n\ntext"; collapse that
    text = re.sub(r"^- *\n+(\S)", r"- \1", text, flags=re.M)
    text = re.sub(r"\n\n(?=\n*- )", "\n", text)            # tighten list spacing
    text = re.sub(r"^(\d+)\. *\n+(\S)", r"\1. \2", text, flags=re.M)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"^ +", "", text, flags=re.M)
    text = re.sub(r" +([,.;:!?)])", r"\1", text)
    text = re.sub(r"^(#{2,3}) (\d{1,2}) (?=[A-Z])", r"\1 \2. ", text, flags=re.M)   # "## 1 Title" -> "## 1. Title"
    # drop hashtags (whole trailing lines, and stray tags at line ends)
    text = re.sub(r"^(?:\s*#\w+\s*)+$", "", text, flags=re.M)
    text = re.sub(r"(?:\s#\w+)+\s*$", "", text, flags=re.M)
    text = lib.no_em_dashes(text)
    return text.strip() + "\n"


def main():
    force = "--force" in sys.argv
    articles = {a["slug"]: a for a in lib.load_articles()}
    built = 0
    for slug, pulse in PULSE.items():
        a = articles[slug]
        src = lib.ROOT / "tools" / "src" / f"{slug}.md"
        if src.exists() and not force:
            print("skip (source exists)", slug); continue
        # read the pre-migration page from git so the script can be re-run after a rebuild
        page = subprocess.run(["git", "show", f"9d3ce01:insights/{slug}/index.html"], capture_output=True, text=True, cwd=lib.ROOT).stdout
        if "article-body" not in page:
            page = (lib.INSIGHTS / slug / "index.html").read_text(encoding="utf-8")
        body = to_markdown(body_html(page))
        summary = a["summary"].replace('"', "'")
        fm = (
            "---\n"
            f"title: {a['title']}\n"
            f"category: {a['category']}\n"
            f"date: {a['date']}\n"
            f"author: {a.get('author', 'Dhananjay Walke')}\n"
            f"linkedin_url: https://www.linkedin.com/pulse/{pulse}/\n"
            "news_based: false\n"
            f"summary: {summary}\n"
            f"slug: {slug}\n"
            "---\n"
        )
        src.write_text(fm + body, encoding="utf-8")
        r = subprocess.run([sys.executable, str(lib.ROOT / "tools" / "new_insight.py"), str(src)], capture_output=True, text=True)
        if r.returncode:
            print("FAILED", slug, r.stderr[-300:]); continue
        built += 1
    print(f"rebuilt {built} articles")


if __name__ == "__main__":
    main()
