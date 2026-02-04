#!/usr/bin/env python3
"""CLI tool to run scraper and analyzer independently."""
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def cmd_scrape(args):
    from database import init_db
    init_db()
    subreddits = args.subreddits.split(",") if args.subreddits else None
    if args.public:
        from scraper_public import scrape_all_public
        result = scrape_all_public(subreddits=subreddits, limit=args.limit)
    else:
        from scraper import run_scrape
        result = run_scrape(subreddits=subreddits, limit=args.limit)
    print(f"\n✅ Scrape complete: {result}")


def cmd_analyze(args):
    from database import init_db
    from analyzer import run_analysis
    init_db()
    result = run_analysis(batch_size=args.batch_size)
    print(f"\n✅ Analysis complete: {result}")


def cmd_run(args):
    """Scrape then analyze."""
    cmd_scrape(args)
    cmd_analyze(args)


def cmd_serve(args):
    import uvicorn
    from database import init_db
    init_db()
    print(f"🚀 Starting API server on http://localhost:{args.port}")
    uvicorn.run("api:app", host="0.0.0.0", port=args.port, reload=args.reload)


def cmd_demo(args):
    """Load sample data for demo mode."""
    from database import init_db
    from demo_data import load_demo_data
    init_db()
    count = load_demo_data()
    print(f"\n✅ Demo mode: loaded {count} sample pain points into the database.")
    print("   Run 'python cli.py serve' to start the API, then open the frontend.")


def cmd_stats(args):
    from database import init_db, get_stats
    init_db()
    stats = get_stats()
    print(f"\n📊 Database Stats:")
    print(f"   Total posts:          {stats['total_posts']}")
    print(f"   Analyzed posts:       {stats['analyzed_posts']}")
    print(f"   Avg opportunity score: {stats['avg_opportunity_score']}")
    print(f"   Top opportunity score: {stats['top_opportunity_score']}")
    print(f"\n   Categories:")
    for c in stats['categories']:
        print(f"     {c['category']}: {c['cnt']}")
    print(f"\n   Subreddits:")
    for s in stats['subreddits']:
        print(f"     r/{s['subreddit']}: {s['cnt']}")


def main():
    parser = argparse.ArgumentParser(description="Reddit Pain Point Discovery Tool")
    sub = parser.add_subparsers(dest="command")

    # scrape
    p_scrape = sub.add_parser("scrape", help="Scrape Reddit for pain points")
    p_scrape.add_argument("--subreddits", "-s", help="Comma-separated subreddit list")
    p_scrape.add_argument("--limit", "-l", type=int, default=50, help="Posts per subreddit")
    p_scrape.add_argument("--public", action="store_true", help="Use public API (no Reddit credentials needed)")

    # analyze
    p_analyze = sub.add_parser("analyze", help="Analyze unanalyzed posts with LLM")
    p_analyze.add_argument("--batch-size", "-b", type=int, default=20, help="Batch size")

    # run (scrape + analyze)
    p_run = sub.add_parser("run", help="Scrape then analyze")
    p_run.add_argument("--subreddits", "-s", help="Comma-separated subreddit list")
    p_run.add_argument("--limit", "-l", type=int, default=50, help="Posts per subreddit")
    p_run.add_argument("--batch-size", "-b", type=int, default=20, help="Batch size")
    p_run.add_argument("--public", action="store_true", help="Use public API (no Reddit credentials needed)")

    # serve
    p_serve = sub.add_parser("serve", help="Start the API server")
    p_serve.add_argument("--port", "-p", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")

    # stats
    sub.add_parser("stats", help="Show database stats")

    # demo
    sub.add_parser("demo", help="Load sample data (no API keys needed)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"scrape": cmd_scrape, "analyze": cmd_analyze, "run": cmd_run, "serve": cmd_serve, "stats": cmd_stats, "demo": cmd_demo}[args.command](args)


if __name__ == "__main__":
    main()
