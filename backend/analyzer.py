"""LLM-powered pain point analyzer using Google Gemini."""
import json
import logging
import time
from google import genai
from config import GOOGLE_API_KEY, CATEGORIES
from database import get_unanalyzed_posts, insert_analysis

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """Analyze this Reddit post for pain points and product opportunities.

**Subreddit:** r/{subreddit}
**Title:** {title}
**Post type:** {post_type}
**Upvotes:** {score}
**Comments:** {num_comments}
**Content:**
{body}

---

Extract the following as JSON (no markdown, just raw JSON):
{{
    "pain_point_summary": "One clear sentence describing the user's pain point or frustration",
    "category": "One of: {categories}",
    "severity": <1-5 integer, where 5 is extreme frustration>,
    "affected_audience": "Who experiences this problem (be specific)",
    "potential_solutions": ["Idea 1: brief description", "Idea 2: brief description", "Idea 3: brief description"],
    "market_size_estimate": "Small|Medium|Large - brief reasoning",
    "existing_solutions": ["Tool 1", "Tool 2"],
    "opportunity_score": <1-100 integer based on: severity * market size * lack of existing solutions * engagement>
}}

Be practical and specific. Focus on actionable software/product ideas.
If the post doesn't contain a clear pain point, set opportunity_score to 10 or below and note that in the summary.
"""


def get_gemini_client():
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured in .env")
    return genai.Client(api_key=GOOGLE_API_KEY)


def analyze_post(client, post: dict) -> dict:
    """Analyze a single post with Gemini."""
    prompt = ANALYSIS_PROMPT.format(
        subreddit=post["subreddit"],
        title=post["title"],
        body=post["body"][:3000],  # Limit context
        post_type=post["post_type"],
        score=post["score"],
        num_comments=post["num_comments"],
        categories=", ".join(CATEGORIES),
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()
        # Clean up markdown code blocks if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        analysis = json.loads(raw_text)
        analysis["raw_llm_response"] = response.text
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response for post {post['id']}: {e}")
        logger.debug(f"Raw response: {response.text if 'response' in dir() else 'N/A'}")
        return {
            "pain_point_summary": "Analysis failed - could not parse LLM response",
            "category": "Other",
            "severity": 1,
            "affected_audience": "Unknown",
            "potential_solutions": [],
            "market_size_estimate": "Unknown",
            "existing_solutions": [],
            "opportunity_score": 0,
            "raw_llm_response": response.text if 'response' in dir() else "",
        }
    except Exception as e:
        logger.error(f"LLM analysis failed for post {post['id']}: {e}")
        return None


def run_analysis(batch_size: int = 20) -> dict:
    """Analyze unanalyzed posts."""
    posts = get_unanalyzed_posts(limit=batch_size)
    if not posts:
        logger.info("No unanalyzed posts found.")
        return {"analyzed": 0, "failed": 0}

    client = get_gemini_client()
    stats = {"analyzed": 0, "failed": 0}

    for post in posts:
        logger.info(f"Analyzing: {post['title'][:60]}...")
        analysis = analyze_post(client, post)

        if analysis:
            insert_analysis(post["id"], analysis)
            stats["analyzed"] += 1
        else:
            stats["failed"] += 1

        # Rate limiting - be gentle with the API
        time.sleep(1)

    logger.info(f"Analysis complete: {stats['analyzed']} analyzed, {stats['failed']} failed")
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = run_analysis()
    print(f"\nAnalysis Results: {stats}")
