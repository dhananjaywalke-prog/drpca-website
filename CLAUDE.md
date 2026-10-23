# drpca.com — LinkedIn-to-Insights auto-publishing brief

**Owner:** CA Dhananjay Walke (DW), Managing Partner, DRP & Co. LLP, Pune
**Purpose of this file:** give Claude Code everything it needs to turn DW's LinkedIn posts into articles on https://drpca.com/insights with no further explanation from DW. Read it fully before touching the repo.
**Last updated:** 22 Oct 2026

---

## 1. The site, in one paragraph

drpca.com is a plain static HTML site (no framework, no build step) hosted on Netlify from the GitHub repo `dhananjaywalke-prog/drpca-website`. Pages are folders with an `index.html`. The Insights section is a listing page at `/insights/` that loads `insights/articles.json` with JavaScript, plus one folder per article at `insights/<slug>/index.html`. Brand: navy `#1F3864`, blue `#2E5FA3`, gold `#B8860B`, fonts DM Serif Display + DM Sans. The tone of every page is factual and premium; the ICAI Code of Ethics governs all copy (section 7).

## 2. Hosting and deployment facts

| Item | Value |
|---|---|
| Netlify project | `drpca`, site id `5ee9646d-3291-4ecb-9607-a784a8adaf74`, team `dhananjaywalke-prog` |
| Primary URL | `https://drpca.com` (apex). `www.drpca.com` 301s to it via `_redirects` |
| Production branch | `main`. Every push to `main` deploys to drpca.com in about 10 seconds |
| Publish directory | `.` (repo root). Build command: none |
| Deploy previews | On, for every pull request: `https://deploy-preview-<PR number>--drpca.netlify.app` |
| Branch deploys | On for all branches: `https://<branch-name-with-slashes-as-dashes>--drpca.netlify.app` |
| Repo visibility | **Public, and it must stay public.** On 21 Oct 2026 making it private silently stopped Netlify receiving pushes (no builds, no previews, no production deploys) and relinking needs a manual OAuth flow DW cannot do alone. Do not make it private again |
| GitHub settings | "Automatically delete head branches" is on; merged branches vanish by themselves |
| DW's local clone | `D:\OneDrive\Documents\GitHub\drpca-website`, managed with GitHub Desktop. DW pulls before editing |
| Netlify Forms | Enabled on the contact page, notifications to dhananjay@drpca.com. Do not touch |
| Other Netlify projects | ems, ems2, desk, dmp subdomains are separate projects. Never deploy to them |

What Claude Code **can** do from a cloud session: clone, branch, commit, push, open PRs via `gh api` (REST only; GraphQL and `gh pr create` are blocked), read Netlify deploy status via the Netlify connector, read GitHub commit statuses (`netlify/drpca/deploy-preview`).
What it **cannot** do: merge PRs, delete branches, change repo settings, change Netlify settings, log in to anything. Those are DW's clicks or already automated.

## 3. The publishing toolkit (already in the repo)

```
tools/new_insight.py          build one article from tools/src/<slug>.md
tools/rebuild_feeds.py        regenerate sitemap.xml + rss.xml from articles.json
tools/clean_legacy.py         one-off clean-up used in Oct 2026; safe to re-run
tools/insights_lib.py         constants: AUTHORS, CATEGORIES, CTA text, disclaimer, feed writers
tools/article_template.html   Jinja template (CSS, nav, footer copied from the site's own article layout)
tools/src/<slug>.md           one Markdown source per article; the front matter is the record of what was published
.claude/commands/new-insight.md   the /new-insight command: rules + steps for one article
```

Requirements: Python 3.9+, `pip install markdown jinja2`.

Run: `python3 tools/new_insight.py tools/src/<slug>.md`. It writes `insights/<slug>/index.html`, updates `insights/articles.json`, `sitemap.xml`, `rss.xml`. Re-running on the same slug overwrites (safe for edits).

`articles.json` entry shape:

```json
{"slug": "...", "title": "...", "date": "2026-10-14", "date_display": "October 14, 2026",
 "category": "Governance", "cat_stripe": "governance", "reading_time": 3,
 "summary": "...", "author": "Dhananjay Walke", "hook": "...", "linkedin_url": "https://..."}
```

Categories (exact strings): `Valuation`, `Regulatory`, `Tax`, `Governance`, `General`.
Authors (keys in `insights_lib.AUTHORS`): `Dhananjay Walke` (byline "CA Dhananjay Walke, Managing Partner, DRP & Co. LLP", photo `/assets/team/dhananjay-walke.jpg`), `Rohan Adkar`.

## 4. Source file format

```markdown
---
title: <search headline: plain, says the subject, under ~90 chars>
hook: <DW's LinkedIn first line, verbatim, bold Unicode converted to plain text>
category: Governance
date: 2026-10-14                 # LinkedIn posting date
author: Dhananjay Walke
linkedin_url: https://www.linkedin.com/feed/update/urn:li:share:7515107323644862464/
news_based: true                 # true if it comments on a reported event about a named company/person
summary: <1-2 plain sentences, <160 chars, no hook, no question; used for card + meta description>
closing_question: <the post's closing question, or a neutral one>
slug: <kebab-case, 6-9 words>
---
Post body in Markdown, DW's words verbatim. Blank line between paragraphs.
## Heading lines only where the post clearly changes section (0-3 per post).

## Background
100-150 words of neutral regulatory context, ending with:
Source: <instrument>, <section> [link](https://official-domain/...)
```

## 5. Rules for turning a post into an article (decided by DW, 21 Oct 2026)

1. **Two headlines.** `title` is for search. `hook` is DW's LinkedIn opener, kept exactly.
2. **Body stays in DW's words.** First person, his sentences, no rephrasing, no padding. Convert `₹` to `Rs.`. No em-dashes anywhere (the script strips them; check the result).
3. **Strip LinkedIn-only lines:** "Your turn 👇", "Repost if…", hashtags, @mentions, emojis, engagement bait. Keep one closing question in `closing_question`.
4. **As-of line.** `news_based: true` for any post about a reported event. Facts about named companies and people are kept exactly as posted; nothing added about them.
5. **Byline:** Managing Partner, DRP & Co. LLP (never "Partner, FCA, IBBI RV"; DW chose the firm role).
6. **Background section:** on by default for Governance, Regulatory and Tax posts when a primary rule is citable. Cite only sebi.gov.in, rbi.org.in, mca.gov.in, incometaxindia.gov.in, ibbi.gov.in, indiacode.nic.in, icai.org. Verify the provision with WebFetch (third-party consolidations such as ca2013.com are acceptable for *checking* wording; the citation itself points to the official site). If it cannot be verified, omit the section and say so in the PR. Never invent a citation.
7. **Do not publish:** wellbeing/personal posts, festival greetings, personal milestones, replies to others, reposts of other people's content, polls, posts that are mainly an image or document with little text, and **all wealth / investing / markets posts** (DW's decision: wealth content stays off the firm site). Also skip anything about VSJC or V S Jadon & Co.; that is a separate entity.
8. **Client check.** If a post names a company, confirm it is not a client of DRP & Co. LLP. Known non-clients as of Oct 2026: Indian Oil, HDFC Bank, Reliance/Jio, Hexaware. Anything else: ask DW in the PR description before merge, and say so in the notification.
9. **Categories.** Governance = boards, directors, succession, related parties, independence. Regulatory = a rule, circular or framework itself (SEBI, RBI, MCA, IBBI). Valuation = anything on value, pricing, DCF, multiples, IPO valuation. Tax = direct/indirect tax. General = everything else that passes rule 7.

## 6. Git workflow (non-negotiable)

- Never commit to `main`. Always: `git checkout main && git pull`, then `git checkout -b insight/<slug>` (or `insights/<yyyy-mm-dd>` for a batch).
- Commit the source `.md`, the generated article folder, `articles.json`, `sitemap.xml`, `rss.xml`. Nothing else.
- Open the PR with `gh api -X POST repos/dhananjaywalke-prog/drpca-website/pulls --input pr.json` (REST). Title `Insight: <title>` or `Insights: <n> articles, <date>`.
- Wait for the commit status `netlify/drpca/deploy-preview` to be `success` (poll `repos/{owner}/{repo}/commits/{sha}/status`), then confirm the article URL on the preview returns the H1.
- Merging is DW's click. Never auto-merge unless section 9 says the hold period has passed and DW has turned that mode on.

## 7. ICAI guardrails (Code of Ethics, 13th edition, applies from 1 April 2026)

No client names or logos. No fees. No superlatives or comparisons with other firms. No awards or rankings. No solicitation beyond the template's own "Get in Touch" box. Language factual and non-sensational. The firm name, FRN W100047, and a link to icai.org are already in the footer; keep them. Articles and blogs are expressly permitted; commentary on public events about listed companies is fine provided rule 8 above is met.

## 8. Reading LinkedIn (the only hard part)

- DW's profile: `https://www.linkedin.com/in/dhananjaywalke/`. Recent posts: `https://www.linkedin.com/in/dhananjaywalke/recent-activity/all/`.
- Post URLs look like `https://www.linkedin.com/feed/update/urn:li:share:<id>/` or `.../urn:li:activity:<id>/`. Either form is fine in `linkedin_url`.
- **WebFetch is blocked by LinkedIn's robots rules and the page needs a login.** The only working method is DW's logged-in Chrome via the Claude in Chrome tools: `navigate` to the URL, then `get_page_text`. The post text appears after DW's headline block and before the reaction counts; comments follow and must be ignored.
- On the recent-activity page, `get_page_text` gives the last ~10 posts with relative dates ("1w", "3d"). Convert relative dates to absolute using today's date; if the post page shows an exact date, prefer that.
- If Chrome is not reachable (no tabs, extension not running, laptop off), stop and tell DW; do not try other routes to LinkedIn.

## 9. Automation: the scheduled task

**Design.** One scheduled task, daily at 21:30 IST on weekdays, requiring DW's computer (so Chrome is reachable). It reads the recent-activity page, compares against what is already published (`linkedin_url` values in `tools/src/*.md` plus `tools/linkedin_skipped.json` for posts deliberately skipped), builds every new eligible post, opens one PR, verifies the preview, and emails DW the links. DW merges from his phone. If nothing new, it does nothing and sends nothing.

**Optional auto-merge mode (off by default).** If DW turns it on, the task also checks PRs it opened earlier: any PR older than 24 hours with a green preview and no comment from DW gets merged. DW can stop a specific article by commenting "hold" on the PR. This is the closest safe approximation of "automatic".

**Dedupe file** `tools/linkedin_skipped.json`: `{"<linkedin_url>": "<reason>"}` for posts judged ineligible, so they are not re-evaluated daily. Commit it with the PR.

**Notification.** Use the Gmail connector to send to dhananjaywalke@gmail.com, subject `drpca.com: <n> article(s) ready for review`, body: one line per article with title, category, preview URL, PR URL, and any flags (unverified Background, client-check question). Plain text, no markdown.

**Prompt for the scheduled task** (paste as the task's prompt; it starts a fresh session each run):

```
You are publishing CA Dhananjay Walke's recent LinkedIn posts as articles on drpca.com.
Clone https://github.com/dhananjaywalke-prog/drpca-website (depth 1) and read CLAUDE.md in full before anything else; it holds the rules, the toolkit and the limits.

1. Open https://www.linkedin.com/in/dhananjaywalke/recent-activity/all/ in Claude in Chrome and read the posts from the last 10 days. If Chrome is not reachable, stop and email dhananjaywalke@gmail.com one line saying the laptop or extension was off; do nothing else.
2. For each post, get its URL and compare against linkedin_url values in tools/src/*.md and keys in tools/linkedin_skipped.json. Skip anything already present.
3. Apply CLAUDE.md section 5 rule 7 (do-not-publish list) and rule 8 (client check). Record ineligible posts in tools/linkedin_skipped.json with a one-line reason.
4. For each eligible post: open the post page, read the full text, write tools/src/<slug>.md per section 4 and the rules in section 5, including a verified Background section where applicable. Run python3 tools/new_insight.py on it. Read the generated article once for stray hashtags, emojis or em-dashes.
5. If at least one article was built: branch insights/<today>, commit the sources, generated folders, articles.json, sitemap.xml, rss.xml and linkedin_skipped.json; push; open one PR via the GitHub REST API; wait for the netlify/drpca/deploy-preview status to succeed; confirm each article URL on the preview returns its H1.
6. Email dhananjaywalke@gmail.com the summary described in CLAUDE.md section 9. If nothing was eligible, send no email.
7. Never push to main. Never merge. Never change repository or Netlify settings.
```

**How DW sets it up (once):** in Claude, ask: "Create a scheduled task named 'drpca Insights from LinkedIn' that runs weekdays at 21:30 IST, requires this computer, and uses the prompt in section 9 of CLAUDE.md in the drpca-website repo." Confirm the approval setting the task is given; it needs automatic approval to run unattended. Keep the laptop on with Chrome and the Claude desktop app open at that hour, or run it by hand with "run the drpca Insights task now".

## 10. Manual mode (works today, no setup)

Send Claude a LinkedIn post URL (or several). It reads them from Chrome, builds the articles on one branch, and replies with the preview and PR links. `/new-insight` in Claude Code does the same from a pasted post.

## 11. Known state as of 22 Oct 2026

- 37 articles live (36 legacy LinkedIn exports from 2020-Apr 2026, cleaned on 21 Oct; 1 new Governance article published 22 Oct).
- Legacy clean-up done: emojis and em-dashes removed, `&amp;amp;` fixed, Article + BreadcrumbList JSON-LD on every article, canonical/og/sitemap on apex host, dead related links removed from the tax article.
- Governance tab added; cards show per-article author.
- Not done (v2 candidates): share image per article, DW author page, applying the sidebar/TOC layout to the 36 legacy articles, `/insights/` pagination once the count passes ~60.
