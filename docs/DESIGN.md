# Reddit Pain Point Discovery Tool — Design Document

## Overview

A tool that automatically scrapes Reddit for user pain points, frustrations, and feature requests, then uses LLM analysis to extract actionable software/product ideas. Results are browsable via a clean web dashboard.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Reddit     │────▶│   Scraper    │────▶│   SQLite    │
│   API/PRAW   │     │   (Python)   │     │   Database  │
└─────────────┘     └──────┬───────┘     └──────┬──────┘
                           │                     │
                    ┌──────▼───────┐             │
                    │  LLM Analysis│             │
                    │  (Gemini)    │             │
                    └──────┬───────┘             │
                           │                     │
                    ┌──────▼───────┐      ┌──────▼──────┐
                    │   FastAPI    │◀─────│   REST API  │
                    │   Backend    │      └──────┬──────┘
                    └──────────────┘             │
                                          ┌──────▼──────┐
                                          │  React SPA  │
                                          │  (Frontend) │
                                          └─────────────┘
```

### Data Flow
1. **Scraper** pulls posts/comments from target subreddits via PRAW
2. **Filter** identifies pain-point language using keyword matching
3. **LLM Pipeline** (Gemini) analyzes filtered posts to extract structured insights
4. **SQLite** stores raw posts, analysis results, and metadata
5. **FastAPI** serves a REST API for the frontend
6. **React SPA** provides a browsable dashboard

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Scraper | Python + PRAW | Best Reddit API wrapper, well-documented |
| LLM | Google Gemini (google-genai) | Already available in the environment |
| Database | SQLite | Zero setup, perfect for side projects |
| Backend API | FastAPI | Modern, fast, auto-generates OpenAPI docs |
| Frontend | React (Vite) | Simple SPA, no SSR needed for this use case |
| Styling | Tailwind CSS | Fast, utility-first, looks great with minimal effort |

## Reddit Data Collection Strategy

### Target Subreddits (configurable)
- r/SaaS, r/startups, r/Entrepreneur, r/smallbusiness
- r/webdev, r/programming, r/productivity
- r/selfhosted, r/sideproject, r/indiehackers
- r/digitalnomad, r/freelance, r/nocode

### Pain Point Detection Keywords
```
"I wish", "frustrated", "annoying", "why isn't there",
"looking for", "need a tool", "hate when", "pain point",
"struggle with", "wish there was", "anyone know of",
"alternative to", "tired of", "can't find", "doesn't exist",
"would pay for", "shut up and take my money", "feature request",
"deal breaker", "broken", "sucks", "terrible", "worst part"
```

### Collection Strategy
- Scrape `hot`, `new`, and `top` (week/month) from each subreddit
- Also search each subreddit with pain-point keywords
- Collect both posts and top-level comments
- Rate-limit aware (PRAW handles this)
- Configurable batch size and frequency

## LLM Analysis Pipeline

Each filtered post/comment is sent to Gemini with a structured prompt:

**Input:** Reddit post text, subreddit, upvotes, comment count
**Output (JSON):**
- `pain_point_summary`: One-line description of the pain point
- `category`: One of [Productivity, Developer Tools, Business, Communication, Finance, Health, Education, Other]
- `severity`: 1-5 scale
- `affected_audience`: Who has this problem
- `potential_solutions`: 2-3 product/feature ideas
- `market_size_estimate`: Small/Medium/Large with reasoning
- `existing_solutions`: Known tools that partially address this
- `opportunity_score`: 1-100 composite score

### Batch Processing
- Process in batches to manage API costs
- Cache results to avoid re-analyzing same posts
- Store raw LLM response for debugging

## Database Schema (SQLite)

```sql
-- Raw scraped posts
CREATE TABLE posts (
    id TEXT PRIMARY KEY,
    reddit_id TEXT UNIQUE,
    subreddit TEXT,
    title TEXT,
    body TEXT,
    author TEXT,
    url TEXT,
    score INTEGER,
    num_comments INTEGER,
    created_utc REAL,
    post_type TEXT, -- 'submission' or 'comment'
    parent_id TEXT, -- for comments
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_analyzed INTEGER DEFAULT 0
);

-- LLM analysis results
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    post_id TEXT REFERENCES posts(id),
    pain_point_summary TEXT,
    category TEXT,
    severity INTEGER,
    affected_audience TEXT,
    potential_solutions TEXT, -- JSON array
    market_size_estimate TEXT,
    existing_solutions TEXT, -- JSON array
    opportunity_score INTEGER,
    raw_llm_response TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraping run metadata
CREATE TABLE scrape_runs (
    id TEXT PRIMARY KEY,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    subreddits TEXT, -- JSON array
    posts_found INTEGER,
    posts_matched INTEGER,
    status TEXT
);
```

## MVP Features

1. ✅ Configurable subreddit scraping
2. ✅ Keyword-based pain point filtering
3. ✅ Gemini-powered analysis and categorization
4. ✅ Opportunity scoring (upvotes × severity × comment engagement)
5. ✅ Web dashboard with filtering and sorting
6. ✅ Pain point cards with full context
7. ✅ Export to JSON/CSV
8. ✅ Trending pain points view

## API Endpoints

```
GET  /api/pain-points          - List pain points (filterable, paginated)
GET  /api/pain-points/:id      - Single pain point detail
GET  /api/stats                - Dashboard stats
GET  /api/categories           - List categories with counts
GET  /api/subreddits           - List subreddits with counts
GET  /api/trending             - Trending pain points
GET  /api/export               - Export as JSON/CSV
POST /api/scrape               - Trigger a scrape run
GET  /api/scrape/status        - Get scraper status
```

## Future Enhancements (Post-MVP)
- Scheduled automatic scraping (cron)
- Duplicate/similar pain point clustering
- Email digest of top new pain points
- Bookmark/star favorite ideas
- Integration with Product Hunt for validation
- Sentiment trend tracking over time
