"""LLM-powered pain point analyzer. Supports Gemini and Claude."""
import json
import logging
import time
from config import GOOGLE_API_KEY, ANTHROPIC_API_KEY, LLM_PROVIDER, CATEGORIES
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


def get_provider():
    """Determine which LLM provider to use."""
    if LLM_PROVIDER == "claude" and ANTHROPIC_API_KEY:
        return "claude"
    elif LLM_PROVIDER == "gemini" and GOOGLE_API_KEY:
        return "gemini"
    elif LLM_PROVIDER == "auto":
        if ANTHROPIC_API_KEY:
            return "claude"
        elif GOOGLE_API_KEY:
            return "gemini"
    raise ValueError("No LLM API key configured. Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in .env")


def analyze_post_claude(client, post: dict) -> dict:
    """Analyze a single post with Claude."""
    prompt = ANALYSIS_PROMPT.format(
        subreddit=post["subreddit"],
        title=post["title"],
        body=post["body"][:3000],
        post_type=post["post_type"],
        score=post["score"],
        num_comments=post["num_comments"],
        categories=", ".join(CATEGORIES),
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        analysis = json.loads(raw_text)
        analysis["raw_llm_response"] = message.content[0].text
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response for post {post['id']}: {e}")
        return {
            "pain_point_summary": "Analysis failed - could not parse LLM response",
            "category": "Other", "severity": 1, "affected_audience": "Unknown",
            "potential_solutions": [], "market_size_estimate": "Unknown",
            "existing_solutions": [], "opportunity_score": 0,
        }
    except Exception as e:
        logger.error(f"Claude analysis failed for post {post['id']}: {e}")
        return None


def analyze_post_gemini(client, post: dict) -> dict:
    """Analyze a single post with Gemini."""
    prompt = ANALYSIS_PROMPT.format(
        subreddit=post["subreddit"],
        title=post["title"],
        body=post["body"][:3000],
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
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        analysis = json.loads(raw_text)
        analysis["raw_llm_response"] = response.text
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response for post {post['id']}: {e}")
        return {
            "pain_point_summary": "Analysis failed - could not parse LLM response",
            "category": "Other", "severity": 1, "affected_audience": "Unknown",
            "potential_solutions": [], "market_size_estimate": "Unknown",
            "existing_solutions": [], "opportunity_score": 0,
        }
    except Exception as e:
        logger.error(f"Gemini analysis failed for post {post['id']}: {e}")
        return None


def run_analysis(batch_size: int = 20) -> dict:
    """Analyze unanalyzed posts."""
    posts = get_unanalyzed_posts(limit=batch_size)
    if not posts:
        logger.info("No unanalyzed posts found.")
        return {"analyzed": 0, "failed": 0}

    provider = get_provider()
    logger.info(f"Using LLM provider: {provider}")

    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        analyze_fn = analyze_post_claude
    else:
        from google import genai
        client = genai.Client(api_key=GOOGLE_API_KEY)
        analyze_fn = analyze_post_gemini

    stats = {"analyzed": 0, "failed": 0}

    for post in posts:
        logger.info(f"Analyzing: {post['title'][:60]}...")
        analysis = analyze_fn(client, post)

        if analysis:
            insert_analysis(post["id"], analysis)
            stats["analyzed"] += 1
        else:
            stats["failed"] += 1

        time.sleep(0.5)

    logger.info(f"Analysis complete: {stats['analyzed']} analyzed, {stats['failed']} failed")
    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = run_analysis()
    print(f"\nAnalysis Results: {stats}")
