"""SQLite database management."""
import sqlite3
import uuid
import json
from pathlib import Path
from contextlib import contextmanager
from config import DATABASE_PATH


def get_db_path():
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


@contextmanager
def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                reddit_id TEXT UNIQUE,
                subreddit TEXT,
                title TEXT,
                body TEXT,
                author TEXT,
                url TEXT,
                score INTEGER DEFAULT 0,
                num_comments INTEGER DEFAULT 0,
                created_utc REAL,
                post_type TEXT,
                parent_id TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_analyzed INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                post_id TEXT REFERENCES posts(id),
                pain_point_summary TEXT,
                category TEXT,
                severity INTEGER,
                affected_audience TEXT,
                potential_solutions TEXT,
                market_size_estimate TEXT,
                existing_solutions TEXT,
                opportunity_score INTEGER,
                raw_llm_response TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS scrape_runs (
                id TEXT PRIMARY KEY,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                subreddits TEXT,
                posts_found INTEGER DEFAULT 0,
                posts_matched INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            );

            CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);
            CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score DESC);
            CREATE INDEX IF NOT EXISTS idx_posts_analyzed ON posts(is_analyzed);
            CREATE INDEX IF NOT EXISTS idx_analyses_category ON analyses(category);
            CREATE INDEX IF NOT EXISTS idx_analyses_score ON analyses(opportunity_score DESC);
        """)


def insert_post(post_data: dict) -> str:
    post_id = str(uuid.uuid4())
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO posts (id, reddit_id, subreddit, title, body, author, url,
                                   score, num_comments, created_utc, post_type, parent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id,
                post_data["reddit_id"],
                post_data["subreddit"],
                post_data.get("title", ""),
                post_data.get("body", ""),
                post_data.get("author", "[deleted]"),
                post_data.get("url", ""),
                post_data.get("score", 0),
                post_data.get("num_comments", 0),
                post_data.get("created_utc", 0),
                post_data.get("post_type", "submission"),
                post_data.get("parent_id"),
            ))
            return post_id
        except sqlite3.IntegrityError:
            # Already exists
            row = conn.execute("SELECT id FROM posts WHERE reddit_id = ?",
                             (post_data["reddit_id"],)).fetchone()
            return row["id"] if row else ""


def insert_analysis(post_id: str, analysis: dict) -> str:
    analysis_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute("""
            INSERT INTO analyses (id, post_id, pain_point_summary, category, severity,
                                  affected_audience, potential_solutions, market_size_estimate,
                                  existing_solutions, opportunity_score, raw_llm_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            post_id,
            analysis.get("pain_point_summary", ""),
            analysis.get("category", "Other"),
            analysis.get("severity", 3),
            analysis.get("affected_audience", ""),
            json.dumps(analysis.get("potential_solutions", [])),
            analysis.get("market_size_estimate", ""),
            json.dumps(analysis.get("existing_solutions", [])),
            analysis.get("opportunity_score", 50),
            analysis.get("raw_llm_response", ""),
        ))
        conn.execute("UPDATE posts SET is_analyzed = 1 WHERE id = ?", (post_id,))
    return analysis_id


def get_pain_points(
    subreddit: str = None,
    category: str = None,
    min_score: int = None,
    sort_by: str = "opportunity_score",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    search: str = None,
):
    query = """
        SELECT p.*, a.pain_point_summary, a.category, a.severity,
               a.affected_audience, a.potential_solutions, a.market_size_estimate,
               a.existing_solutions, a.opportunity_score, a.analyzed_at
        FROM posts p
        JOIN analyses a ON a.post_id = p.id
        WHERE 1=1
    """
    params = []

    if subreddit:
        query += " AND p.subreddit = ?"
        params.append(subreddit)
    if category:
        query += " AND a.category = ?"
        params.append(category)
    if min_score is not None:
        query += " AND a.opportunity_score >= ?"
        params.append(min_score)
    if search:
        query += " AND (p.title LIKE ? OR p.body LIKE ? OR a.pain_point_summary LIKE ?)"
        params.extend([f"%{search}%"] * 3)

    valid_sorts = {
        "opportunity_score": "a.opportunity_score",
        "score": "p.score",
        "created_utc": "p.created_utc",
        "severity": "a.severity",
        "num_comments": "p.num_comments",
    }
    sort_col = valid_sorts.get(sort_by, "a.opportunity_score")
    order_dir = "DESC" if order.lower() == "desc" else "ASC"
    query += f" ORDER BY {sort_col} {order_dir} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        # Get total count
        count_query = query.split("ORDER BY")[0].replace("SELECT p.*, a.*", "SELECT COUNT(*)")
        count_query = "SELECT COUNT(*) as cnt FROM posts p JOIN analyses a ON a.post_id = p.id WHERE 1=1"
        count_params = []
        if subreddit:
            count_query += " AND p.subreddit = ?"
            count_params.append(subreddit)
        if category:
            count_query += " AND a.category = ?"
            count_params.append(category)
        if min_score is not None:
            count_query += " AND a.opportunity_score >= ?"
            count_params.append(min_score)
        if search:
            count_query += " AND (p.title LIKE ? OR p.body LIKE ? OR a.pain_point_summary LIKE ?)"
            count_params.extend([f"%{search}%"] * 3)
        total = conn.execute(count_query, count_params).fetchone()["cnt"]

    return [dict(r) for r in rows], total


def get_pain_point_by_id(post_id: str):
    with get_db() as conn:
        row = conn.execute("""
            SELECT p.*, a.pain_point_summary, a.category, a.severity,
                   a.affected_audience, a.potential_solutions, a.market_size_estimate,
                   a.existing_solutions, a.opportunity_score, a.analyzed_at,
                   a.raw_llm_response
            FROM posts p
            JOIN analyses a ON a.post_id = p.id
            WHERE p.id = ?
        """, (post_id,)).fetchone()
    return dict(row) if row else None


def get_stats():
    with get_db() as conn:
        total_posts = conn.execute("SELECT COUNT(*) as cnt FROM posts").fetchone()["cnt"]
        analyzed = conn.execute("SELECT COUNT(*) as cnt FROM posts WHERE is_analyzed = 1").fetchone()["cnt"]
        categories = conn.execute("""
            SELECT category, COUNT(*) as cnt
            FROM analyses GROUP BY category ORDER BY cnt DESC
        """).fetchall()
        subreddits = conn.execute("""
            SELECT subreddit, COUNT(*) as cnt
            FROM posts WHERE is_analyzed = 1 GROUP BY subreddit ORDER BY cnt DESC
        """).fetchall()
        avg_score = conn.execute("SELECT AVG(opportunity_score) as avg FROM analyses").fetchone()["avg"]
        top_score = conn.execute("SELECT MAX(opportunity_score) as mx FROM analyses").fetchone()["mx"]

    return {
        "total_posts": total_posts,
        "analyzed_posts": analyzed,
        "categories": [dict(c) for c in categories],
        "subreddits": [dict(s) for s in subreddits],
        "avg_opportunity_score": round(avg_score, 1) if avg_score else 0,
        "top_opportunity_score": top_score or 0,
    }


def get_unanalyzed_posts(limit: int = 20):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM posts WHERE is_analyzed = 0 ORDER BY score DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_trending(limit: int = 10):
    """Get pain points trending by recency + engagement."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT p.*, a.pain_point_summary, a.category, a.severity,
                   a.affected_audience, a.potential_solutions, a.market_size_estimate,
                   a.existing_solutions, a.opportunity_score, a.analyzed_at
            FROM posts p
            JOIN analyses a ON a.post_id = p.id
            ORDER BY (p.score * 2 + p.num_comments * 3 + a.opportunity_score) DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]
