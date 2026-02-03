# 🎯 Reddit Pain Point Discovery Tool

> Discover software product ideas by mining Reddit for user pain points. AI-powered analysis with Google Gemini.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![React](https://img.shields.io/badge/React-19-blue) ![SQLite](https://img.shields.io/badge/SQLite-3-orange) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

<!-- TODO: Add a hero screenshot here -->
<!-- ![Dashboard Screenshot](docs/screenshot.png) -->

## Why This Tool?

Finding product ideas shouldn't be guesswork. Every day, thousands of people describe their frustrations on Reddit — "I wish there was...", "Why isn't there a tool for...", "I'd pay for something that...". These are **validated pain points** from real users.

This tool **automates the discovery process**:
- Scrapes targeted subreddits for posts expressing frustration or unmet needs
- Uses AI to extract structured insights (pain point, audience, market size, solutions)
- Ranks opportunities by a composite score so you can focus on the best ones
- Presents everything in a clean, filterable dashboard

**Stop building products nobody wants. Start with real pain.**

## How It Works

1. **Scrapes** posts and comments from 12+ target subreddits (r/SaaS, r/startups, r/Entrepreneur, etc.)
2. **Filters** for pain-point language ("I wish", "frustrated", "need a tool", etc.)
3. **Analyzes** each match with Google Gemini to extract structured insights
4. **Ranks** opportunities by a composite score (engagement × severity × market potential)
5. **Displays** everything in a clean, filterable dashboard

## Features

- [x] 🔍 **Smart Scraping** — Targets 12+ subreddits with pain-point keyword matching
- [x] 🤖 **AI Analysis** — Gemini extracts pain points, audiences, solutions, market estimates
- [x] 📊 **Opportunity Scoring** — Composite score based on engagement, severity, and market size
- [x] 🏷️ **Auto-Categorization** — Productivity, Dev Tools, Business, Marketing, etc.
- [x] 🔥 **Trending View** — See what's hot right now
- [x] 🔎 **Search & Filter** — By subreddit, category, score, keywords
- [x] 📥 **Export** — CSV and JSON export
- [x] 🚀 **One-Click Scrape** — Trigger scrapes from the dashboard UI
- [x] 🎮 **Demo Mode** — Try the dashboard with sample data, no API keys needed
- [ ] ⏰ Scheduled scraping (cron jobs)
- [ ] 📧 Email/Slack alerts for high-score opportunities
- [ ] 📈 Trend detection over time
- [ ] 🌐 Multi-platform support (Hacker News, Twitter/X, Indie Hackers)
- [ ] 🏷️ Custom keyword lists
- [ ] 📊 Analytics dashboard with charts

## Quick Start

### Try It Instantly (Demo Mode)

No API keys needed — explore the dashboard with sample data:

```bash
git clone https://github.com/lefttree/reddit-pain-points.git
cd reddit-pain-points

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python cli.py demo    # Load 10 sample pain points
python cli.py serve & # Start API on :8000
cd ..

# Frontend
cd frontend
npm install
npm run dev           # Start UI on :5173
```

Open **http://localhost:5173** and explore!

### Full Setup (With Reddit + Gemini)

#### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- Reddit API credentials ([create app here](https://www.reddit.com/prefs/apps))
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

#### 2. Install & Configure

```bash
git clone https://github.com/lefttree/reddit-pain-points.git
cd reddit-pain-points

# Copy and fill in your credentials
cp .env.example .env
# Edit .env with your Reddit and Gemini API keys

# Install backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend
cd frontend
npm install
cd ..
```

#### 3. Run the Scraper

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

#### 4. Start the Dashboard

```bash
# Option A: Quick start (both services)
./run.sh

# Option B: Manual
cd backend && python cli.py serve &    # API on :8000
cd frontend && npm run dev &           # UI on :5173
```

Open **http://localhost:5173** to browse discovered pain points.

## Example Output

Here's what an analyzed pain point looks like:

```
🎯 Pain Point: "No simple tool to aggregate feature requests from multiple
   channels (email, Slack, support, social) for small teams"

📊 Opportunity Score: 82/100
🔥 Severity: 4/5
👥 Audience: Small SaaS founders and product managers
📈 Market Size: Large

💡 Product Ideas:
   1. Lightweight feature request aggregator with email/Slack/Twitter integrations
   2. AI-powered request deduplication and ranking tool
   3. Simple voting board with multi-channel intake automation

🔍 Existing Solutions: Canny, Productboard, Nolt, Fider
📌 Source: r/SaaS · ⬆ 187 · 💬 43 comments
```

## Project Structure

```
reddit-pain-points/
├── backend/
│   ├── api.py           # FastAPI REST API
│   ├── scraper.py       # Reddit scraper (PRAW)
│   ├── analyzer.py      # Gemini LLM analyzer
│   ├── database.py      # SQLite management
│   ├── config.py        # Configuration
│   ├── cli.py           # CLI interface
│   ├── demo_data.py     # Sample data for demo mode
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main React app
│   │   ├── main.jsx     # Entry point
│   │   └── index.css    # Tailwind styles
│   ├── package.json
│   └── vite.config.js
├── data/                # SQLite database (auto-created)
├── docs/
│   └── DESIGN.md        # Architecture & design doc
├── .env.example         # Template for credentials
├── run.sh               # Quick start script
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
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
GOOGLE_API_KEY=your_gemini_api_key

# Optional
SUBREDDITS=SaaS,startups,Entrepreneur  # Override target subreddits
SCRAPE_LIMIT=50                         # Posts per subreddit per feed
DATABASE_PATH=data/painpoints.db        # Database location
```

### Reddit App Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Choose **"script"** type
4. Set redirect URI to `http://localhost:8080`
5. Copy the client ID (under app name) and secret

## Roadmap

- **Scheduled Scraping** — Cron-based scraping with configurable intervals
- **Alerts** — Email/Slack notifications when high-scoring opportunities are found
- **Multi-Platform** — Extend to Hacker News, Twitter/X, Indie Hackers, Product Hunt
- **Trend Detection** — Track pain points over time, detect emerging trends
- **Custom Keywords** — User-defined keyword lists for domain-specific discovery
- **Team Features** — Bookmarks, notes, and collaboration on opportunities
- **Analytics Dashboard** — Charts and visualizations for scraping history

## Tech Stack

- **Backend:** Python, FastAPI, PRAW, Google Gemini, SQLite
- **Frontend:** React 19, Vite, Tailwind CSS
- **Analysis:** Google Gemini 2.0 Flash

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
