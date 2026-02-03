# Contributing to Reddit Pain Point Discovery Tool

Thanks for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Development Setup

1. **Fork and clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/reddit-pain-points.git
   cd reddit-pain-points
   ```

2. **Set up the backend:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Set up the frontend:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

5. **Run in demo mode (no API keys needed):**
   ```bash
   cd backend
   python cli.py demo
   python cli.py serve &
   cd ../frontend
   npm run dev
   ```

## 📝 How to Contribute

### Reporting Bugs

- Use the [Bug Report](https://github.com/seanli/reddit-pain-points/issues/new?template=bug_report.md) issue template
- Include steps to reproduce, expected behavior, and actual behavior
- Include your Python/Node.js version and OS

### Suggesting Features

- Use the [Feature Request](https://github.com/seanli/reddit-pain-points/issues/new?template=feature_request.md) issue template
- Explain the use case and why it would be valuable

### Submitting Pull Requests

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. Make your changes and test them

3. Write clear commit messages:
   ```
   feat: add email notification for high-score pain points
   fix: handle deleted Reddit posts gracefully
   docs: update API endpoint documentation
   ```

4. Push and open a PR:
   ```bash
   git push origin feature/my-awesome-feature
   ```

5. In the PR description:
   - Describe what the change does
   - Link any related issues
   - Include screenshots for UI changes

## 🎨 Code Style

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for function parameters and return types
- Add docstrings to all public functions
- Keep functions focused and under ~50 lines
- Use f-strings for string formatting

```python
def analyze_post(client, post: dict) -> dict:
    """Analyze a single Reddit post for pain points using Gemini.
    
    Args:
        client: Google Gemini client instance.
        post: Dictionary containing post data (title, body, subreddit, etc.)
    
    Returns:
        Dictionary with analysis results including pain_point_summary,
        category, severity, and opportunity_score.
    """
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Use Tailwind CSS for styling (no inline styles or CSS modules)
- Keep components under ~100 lines; extract sub-components when needed
- Use `const` by default, `let` when reassignment is needed

### General

- No hardcoded credentials or personal paths
- All configuration should go through `.env` / `config.py`
- Keep dependencies minimal — don't add a library for something simple

## 📁 Project Structure

```
reddit-pain-points/
├── backend/          # Python API + scraper + analyzer
│   ├── api.py        # FastAPI REST endpoints
│   ├── scraper.py    # Reddit scraping logic
│   ├── analyzer.py   # Gemini LLM analysis
│   ├── database.py   # SQLite operations
│   ├── config.py     # Configuration management
│   └── cli.py        # CLI interface
├── frontend/         # React + Vite + Tailwind
│   └── src/
│       └── App.jsx   # Main application
└── data/             # SQLite database (gitignored)
```

## 🧪 Testing

Currently, there are no automated tests (contributions welcome!). Before submitting:

- Test the full pipeline: `python cli.py run`
- Verify the API: `python cli.py serve` → check `http://localhost:8000/docs`
- Check the frontend: `npm run dev` → verify the dashboard works
- Try demo mode: `python cli.py demo` → ensure sample data loads

## 💬 Questions?

Open a [Discussion](https://github.com/seanli/reddit-pain-points/discussions) or an issue. We're happy to help!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
