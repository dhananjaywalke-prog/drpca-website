#!/usr/bin/env python3
"""Regenerate sitemap.xml and rss.xml from insights/articles.json.

Run after editing articles.json by hand. new_insight.py calls this automatically.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insights_lib as lib  # noqa: E402

if __name__ == "__main__":
    lib.rebuild_feeds()
    print("wrote sitemap.xml and rss.xml")
