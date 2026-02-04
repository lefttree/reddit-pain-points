"""Reddit scraper using public JSON API (no authentication needed)."""
import re
import time
import logging
import httpx
from datetime import datetime
from config import SUBREDDITS, SCRAPE_LIMIT, PAIN_KEYWORDS
from database import insert_post

logger = logging.getLogger(__name__)

USER_AGENT = "pain-point-discovery/1.0 (research tool)"
BASE_URL = "https://www.reddit.com"
REQUEST_DELAY = 2  # Reddit rate limits unauthenticated to ~10 req/min


def matches_pain_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in PAIN_KEYWORDS)


def scrape_subreddit_public(subreddit_name: str, limit: int = SCRAPE_LIMIT) -> dict:
    """Scrape a subreddit using Reddit's public JSON API."""
    stats = {"found": 0, "matched": 0, "errors": 0}
    client = httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True)

    # Search with pain-point keywords
    search_terms = ["frustrated", "i wish", "need a tool", "looking for", "annoying",
                    "alternative to", "why isn't there", "would pay for", "tired of",
                    "can't find", "doesn't exist", "pain point"]

    seen_ids = set()

    for term in search_terms:
        try:
            url = f"{BASE_URL}/r/{subreddit_name}/search.json"
            params = {
                "q": term,
                "restrict_sr": "on",
                "sort": "relevance",
                "t": "month",
                "limit": min(limit, 25),
            }
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                logger.warning(f"  HTTP {resp.status_code} for r/{subreddit_name} search '{term}'")
                stats["errors"] += 1
                time.sleep(REQUEST_DELAY)
                continue

            data = resp.json()
            posts = data.get("data", {}).get("children", [])

            for post in posts:
                pd = post.get("data", {})
                post_id = pd.get("name", "")

                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)
                stats["found"] += 1

                title = pd.get("title", "")
                body = pd.get("selftext", "")
                full_text = f"{title} {body}"

                if not matches_pain_keywords(full_text):
                    continue

                stats["matched"] += 1
                insert_post({
                    "reddit_id": post_id,
                    "subreddit": subreddit_name,
                    "title": title,
                    "body": body[:5000],
                    "author": pd.get("author", "[deleted]"),
                    "url": f"https://reddit.com{pd.get('permalink', '')}",
                    "score": pd.get("score", 0),
                    "num_comments": pd.get("num_comments", 0),
                    "created_utc": pd.get("created_utc", 0),
                    "post_type": "submission",
                    "parent_id": None,
                })

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logger.error(f"  Error searching r/{subreddit_name} for '{term}': {e}")
            stats["errors"] += 1
            time.sleep(REQUEST_DELAY)

    client.close()
    return stats


def scrape_all_public(subreddits: list = None, limit: int = SCRAPE_LIMIT) -> dict:
    """Scrape all configured subreddits using public API."""
    subs = subreddits or SUBREDDITS
    total_stats = {"found": 0, "matched": 0, "errors": 0}

    logger.info(f"🔍 Scraping {len(subs)} subreddits (public API, no auth needed)")
    for sub_name in subs:
        logger.info(f"  📌 r/{sub_name}...")
        stats = scrape_subreddit_public(sub_name, limit)
        logger.info(f"     Found {stats['found']}, matched {stats['matched']}")
        for k in total_stats:
            total_stats[k] += stats[k]

    logger.info(f"✅ Done! Total: {total_stats['found']} found, {total_stats['matched']} matched pain points")
    return total_stats
