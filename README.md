# 🎯 Reddit Pain Point Discovery Tool

Automatically scrapes Reddit for user pain points and frustrations, analyzes them with AI (Gemini), and surfaces actionable software/product ideas through a clean web dashboard.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![React](https://img.shields.io/badge/React-19-blue) ![SQLite](https://img.shields.io/badge/SQLite-3-orange)

## How It Works

1. **Scrapes** posts and comments from target subreddits (r/SaaS, r/startups, r/Entrepreneur, etc.)
2. **Filters** for pain-point language ("I wish", "frustrated", "need a tool", etc.)
3. **Analyzes** each match with Google Gemini to extract structured insights
4. **Ranks** opportunities by a composite score (engagement × severity × market potential)
5. **Displays** everything in a clean, filterable dashboard

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- Reddit API credentials ([create app here](https://www.reddit.com/prefs/apps))
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### 2. Setup

```bash
# Clone/enter the project
cd reddit-pain-points

# Copy and fill in your credentials
cp .env.example .env
# Edit .env with your Reddit and Gemini API keys

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Run the Scraper

```bash
cd backend

# Scrape Reddit + analyze with AI (full pipeline)
python cli.py run

# Or run steps separately:
python cli.py scrape                    # Just scrape
python cli.py analyze                   # Just analyze unanalyzed posts
python cli.py scrape -s "SaaS,startups" # Specific subreddits
python cli.py stats                     # View database stats
```

### 4. Start the Dashboard

```bash
# Option A: Quick start (both services)
./run.sh

# Option B: Manual
cd backend && python cli.py serve &    # API on :8000
cd frontend && npm run dev &           # UI on :3000
```

Open **http://localhost:3000** to browse discovered pain points.

## Features

- **🔍 Smart Scraping** — Targets 12+ subreddits, searches with pain-point keywords
- **🤖 AI Analysis** — Gemini extracts pain points, audiences, solutions, market estimates
- **📊 Opportunity Scoring** — Composite score based on engagement, severity, and market size
- **🏷️ Categorization** — Auto-categorized (Productivity, Dev Tools, Business, etc.)
- **🔥 Trending View** — See what's hot right now
- **🔎 Search & Filter** — By subreddit, category, score, keywords
- **📥 Export** — CSV and JSON export
- **🚀 One-Click Scrape** — Trigger scrapes from the UI

## Project Structure

```
reddit-pain-points/
├── backend/
│   ├── api.py          # FastAPI REST API
│   ├── scraper.py      # Reddit scraper (PRAW)
│   ├── analyzer.py     # Gemini LLM analyzer
│   ├── database.py     # SQLite management
│   ├── config.py       # Configuration
│   ├── cli.py          # CLI interface
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx     # Main React app
│   │   ├── main.jsx    # Entry point
│   │   └── index.css   # Tailwind styles
│   ├── package.json
│   └── vite.config.js
├── data/               # SQLite database (auto-created)
├── docs/
│   └── DESIGN.md       # Architecture & design doc
├── .env.example        # Template for credentials
├── run.sh              # Quick start script
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pain-points` | List pain points (filterable, paginated) |
| GET | `/api/pain-points/:id` | Single pain point detail |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/trending` | Trending pain points |
| GET | `/api/categories` | Categories with counts |
| GET | `/api/subreddits` | Subreddits with counts |
| GET | `/api/export?format=csv` | Export data |
| POST | `/api/scrape` | Trigger scrape run |
| GET | `/api/scrape/status` | Scraper status |

Auto-generated docs at **http://localhost:8000/docs** (Swagger UI).

## Configuration

All config via `.env`:

```bash
# Required
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
GOOGLE_API_KEY=...

# Optional
SUBREDDITS=SaaS,startups,Entrepreneur  # Override target subreddits
SCRAPE_LIMIT=50                         # Posts per subreddit per feed
DATABASE_PATH=data/painpoints.db        # Database location
```

## Reddit App Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Choose **"script"** type
4. Set redirect URI to `http://localhost:8080`
5. Copy the client ID (under app name) and secret

## Tech Stack

- **Backend:** Python, FastAPI, PRAW, Google Gemini, SQLite
- **Frontend:** React 19, Vite, Tailwind CSS
- **Analysis:** Google Gemini 2.0 Flash

## License

MIT — do whatever you want with it.
