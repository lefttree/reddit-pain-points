"""Reddit scraper using PRAW."""
import re
import time
import logging
from datetime import datetime
import praw
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    SUBREDDITS, SCRAPE_LIMIT, PAIN_KEYWORDS,
)
from database import insert_post

logger = logging.getLogger(__name__)


def get_reddit_client() -> praw.Reddit:
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        raise ValueError(
            "Reddit API credentials not configured. "
            "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
        )
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )


def matches_pain_keywords(text: str) -> bool:
    """Check if text contains pain-point language."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in PAIN_KEYWORDS)


def scrape_subreddit(reddit: praw.Reddit, subreddit_name: str, limit: int = SCRAPE_LIMIT) -> dict:
    """Scrape a single subreddit for pain-point posts."""
    stats = {"found": 0, "matched": 0}
    sub = reddit.subreddit(subreddit_name)

    # Collect from multiple feeds
    seen_ids = set()
    submissions = []

    try:
        for source_name, source in [
            ("hot", sub.hot(limit=limit)),
            ("new", sub.new(limit=limit)),
            ("top_week", sub.top(time_filter="week", limit=limit)),
        ]:
            for submission in source:
                if submission.id not in seen_ids:
                    seen_ids.add(submission.id)
                    submissions.append(submission)

        # Also search with pain keywords (top 5 most distinctive ones)
        search_keywords = ["I wish", "frustrated with", "need a tool", "looking for", "alternative to"]
        for kw in search_keywords:
            try:
                for submission in sub.search(kw, limit=min(limit, 25), sort="relevance", time_filter="month"):
                    if submission.id not in seen_ids:
                        seen_ids.add(submission.id)
                        submissions.append(submission)
            except Exception as e:
                logger.warning(f"Search failed for '{kw}' in r/{subreddit_name}: {e}")

    except Exception as e:
        logger.error(f"Failed to scrape r/{subreddit_name}: {e}")
        return stats

    for submission in submissions:
        stats["found"] += 1
        full_text = f"{submission.title} {submission.selftext}"

        if matches_pain_keywords(full_text):
            stats["matched"] += 1
            post_id = insert_post({
                "reddit_id": f"t3_{submission.id}",
                "subreddit": subreddit_name,
                "title": submission.title,
                "body": submission.selftext[:5000],  # Truncate very long posts
                "author": str(submission.author) if submission.author else "[deleted]",
                "url": f"https://reddit.com{submission.permalink}",
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "post_type": "submission",
            })

            # Also check top comments
            try:
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:10]:
                    if hasattr(comment, 'body') and matches_pain_keywords(comment.body):
                        insert_post({
                            "reddit_id": f"t1_{comment.id}",
                            "subreddit": subreddit_name,
                            "title": submission.title,
                            "body": comment.body[:3000],
                            "author": str(comment.author) if comment.author else "[deleted]",
                            "url": f"https://reddit.com{comment.permalink}",
                            "score": comment.score,
                            "num_comments": 0,
                            "created_utc": comment.created_utc,
                            "post_type": "comment",
                            "parent_id": f"t3_{submission.id}",
                        })
                        stats["matched"] += 1
            except Exception as e:
                logger.warning(f"Failed to process comments for {submission.id}: {e}")

    logger.info(f"r/{subreddit_name}: found {stats['found']} posts, {stats['matched']} matched pain keywords")
    return stats


def run_scrape(subreddits: list[str] = None, limit: int = SCRAPE_LIMIT) -> dict:
    """Run a full scrape across all configured subreddits."""
    subreddits = subreddits or SUBREDDITS
    reddit = get_reddit_client()

    total_stats = {"found": 0, "matched": 0, "subreddits_scraped": 0}

    for sub_name in subreddits:
        sub_name = sub_name.strip()
        if not sub_name:
            continue
        logger.info(f"Scraping r/{sub_name}...")
        stats = scrape_subreddit(reddit, sub_name, limit)
        total_stats["found"] += stats["found"]
        total_stats["matched"] += stats["matched"]
        total_stats["subreddits_scraped"] += 1
        time.sleep(1)  # Be nice to Reddit's API

    logger.info(
        f"Scrape complete: {total_stats['subreddits_scraped']} subreddits, "
        f"{total_stats['found']} posts found, {total_stats['matched']} matched"
    )
    return total_stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = run_scrape()
    print(f"\nScrape Results: {stats}")
