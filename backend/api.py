"""FastAPI REST API for the pain point dashboard."""
import json
import csv
import io
import logging
import threading
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from database import (
    init_db, get_pain_points, get_pain_point_by_id,
    get_stats, get_trending,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reddit Pain Point Discovery", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track scraper status
scraper_status = {"running": False, "last_result": None}


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized.")


@app.get("/api/pain-points")
def list_pain_points(
    subreddit: str = None,
    category: str = None,
    min_score: int = None,
    sort_by: str = "opportunity_score",
    order: str = "desc",
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    search: str = None,
):
    items, total = get_pain_points(
        subreddit=subreddit,
        category=category,
        min_score=min_score,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
        search=search,
    )
    # Parse JSON fields
    for item in items:
        for field in ["potential_solutions", "existing_solutions"]:
            if isinstance(item.get(field), str):
                try:
                    item[field] = json.loads(item[field])
                except (json.JSONDecodeError, TypeError):
                    item[field] = []
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@app.get("/api/pain-points/{post_id}")
def get_pain_point(post_id: str):
    item = get_pain_point_by_id(post_id)
    if not item:
        return {"error": "Not found"}, 404
    for field in ["potential_solutions", "existing_solutions"]:
        if isinstance(item.get(field), str):
            try:
                item[field] = json.loads(item[field])
            except (json.JSONDecodeError, TypeError):
                item[field] = []
    return item


@app.get("/api/stats")
def stats():
    return get_stats()


@app.get("/api/trending")
def trending(limit: int = Query(default=10, le=50)):
    items = get_trending(limit=limit)
    for item in items:
        for field in ["potential_solutions", "existing_solutions"]:
            if isinstance(item.get(field), str):
                try:
                    item[field] = json.loads(item[field])
                except (json.JSONDecodeError, TypeError):
                    item[field] = []
    return {"items": items}


@app.get("/api/categories")
def categories():
    st = get_stats()
    return {"categories": st["categories"]}


@app.get("/api/subreddits")
def subreddits():
    st = get_stats()
    return {"subreddits": st["subreddits"]}


@app.get("/api/export")
def export(format: str = "json"):
    items, _ = get_pain_points(limit=10000, offset=0)
    for item in items:
        for field in ["potential_solutions", "existing_solutions"]:
            if isinstance(item.get(field), str):
                try:
                    item[field] = json.loads(item[field])
                except (json.JSONDecodeError, TypeError):
                    item[field] = []

    if format == "csv":
        output = io.StringIO()
        if items:
            writer = csv.DictWriter(output, fieldnames=items[0].keys())
            writer.writeheader()
            for item in items:
                row = {k: json.dumps(v) if isinstance(v, list) else v for k, v in item.items()}
                writer.writerow(row)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=pain_points.csv"},
        )
    return {"items": items, "count": len(items)}


@app.post("/api/scrape")
def trigger_scrape():
    if scraper_status["running"]:
        return {"status": "already_running"}

    def _run():
        scraper_status["running"] = True
        try:
            from scraper import run_scrape
            from analyzer import run_analysis
            scrape_result = run_scrape()
            analysis_result = run_analysis(batch_size=50)
            scraper_status["last_result"] = {
                "scrape": scrape_result,
                "analysis": analysis_result,
            }
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            scraper_status["last_result"] = {"error": str(e)}
        finally:
            scraper_status["running"] = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"status": "started"}


@app.get("/api/scrape/status")
def scrape_status():
    return scraper_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
