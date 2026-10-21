---
description: Turn a pasted LinkedIn post by DW into an Insights article on drpca.com, on a review branch with a Netlify deploy preview.
---

You are publishing one of CA Dhananjay Walke's LinkedIn posts as an article on drpca.com/insights.
The post text, its LinkedIn URL and posting date are in `$ARGUMENTS` or in the message that invoked this command. If any of the three is missing, ask for it before doing anything else.

## Step 0. Gate

Refuse (politely, one sentence) and stop if the post is any of: a wellbeing or personal post, a festival greeting, a personal milestone, a reply to someone else, or a wealth / investing / markets post. Wealth-pillar posts do not go on the firm website (DW's decision, 21 Oct 2026). Everything else proceeds.

Also stop and ask if the post names a company and you are not sure it is not a client of DRP & Co. LLP. Client names may not appear on the website (ICAI Code of Ethics).

## Step 1. Write the source file

Create `tools/src/<slug>.md` in the format documented at the top of `tools/new_insight.py`. Rules:

1. **Two headlines.** `title` is the search headline: plain, says the subject ("When a relative's business ends an independent director's term: SEBI's 50 lakh test"). `hook` is DW's LinkedIn first line, kept exactly.
2. **Body stays in DW's words.** First person, short paragraphs, his sentences. Do not pad, rephrase or "improve". Add `## Heading` lines only where the post clearly changes section; many posts need none. No em-dashes anywhere (the script also strips them).
3. **Remove LinkedIn-only lines:** "Your turn 👇", "Repost if…", hashtags, @mentions, emoji. Put one closing question from the post (or a neutral one) in `closing_question`.
4. **`news_based: true`** whenever the post comments on a reported event about a named company or person. Facts about them are kept exactly as posted. Add nothing about them that is not in the post.
5. **Category:** Governance (boards, directors, succession, related parties), Valuation, Regulatory (a rule or circular itself), Tax, General.
6. **`summary`:** one or two plain sentences for the listing card and meta description, under 160 characters, no hook, no question.
7. **`## Background` section** (DW's decision, 21 Oct 2026): include it for Governance, Regulatory and Tax posts when there is a citable primary rule; skip it for General posts or when there is none. 100 to 150 words, neutral reference register, stating the regulation, section and date. End with `Source: <name of instrument>, <section> [link](https://official-domain/...)`. Only cite sebi.gov.in, rbi.org.in, mca.gov.in, incometaxindia.gov.in, ibbi.gov.in, indiacode.nic.in or icai.org. If you cannot verify the provision from one of those sources with WebFetch, leave the section out and say so. Never invent a citation.
8. **ICAI check** before writing: no client names, no claims of superiority over other firms, no fees, no solicitation beyond the template's own call-to-action. Flag anything borderline to DW rather than editing it silently.

## Step 2. Build

```
git checkout main && git pull
git checkout -b insight/<slug>
python3 tools/new_insight.py tools/src/<slug>.md
```

Open the generated `insights/<slug>/index.html` and read the article body once for broken Markdown, stray hashtags, or an em-dash the script missed.

## Step 3. Commit, push, preview

```
git add tools/src/<slug>.md insights/<slug>/ insights/articles.json sitemap.xml rss.xml
git commit -m "Insight: <title>"
git push -u origin insight/<slug>
gh pr create --title "Insight: <title>" --body "Preview, then merge to publish." --base main
```

Netlify builds a deploy preview for the pull request within about a minute. Give DW the PR link and the preview URL (`https://deploy-preview-<PR number>--drpca.netlify.app/insights/<slug>/`) in one line each, plus a short list of anything you flagged in Step 1.

Never push to `main` directly. DW merges the PR after reading the preview; the merge is the publish.
