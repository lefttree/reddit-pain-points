"""Generate sample data for demo mode.

Creates a small SQLite database with ~10 example pain points so users
can explore the dashboard without needing Reddit or Gemini API credentials.
"""
import json
import uuid
import time
from database import init_db, insert_post, insert_analysis

SAMPLE_PAIN_POINTS = [
    {
        "post": {
            "reddit_id": "t3_demo_001",
            "subreddit": "SaaS",
            "title": "I wish there was a simple way to track feature requests from multiple channels",
            "body": "We get feature requests via email, Slack, support tickets, and Twitter. I've tried Canny and Productboard but they're either too expensive or too complex for a small team. I just want a simple tool that aggregates requests and lets me see what's most popular. Would pay $20-50/mo for this.",
            "author": "startup_founder_42",
            "url": "https://reddit.com/r/SaaS/comments/demo001",
            "score": 187,
            "num_comments": 43,
            "created_utc": time.time() - 86400 * 2,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "No simple, affordable tool to aggregate feature requests from multiple channels (email, Slack, support, social) for small teams",
            "category": "Productivity",
            "severity": 4,
            "affected_audience": "Small SaaS founders and product managers managing feature requests across multiple channels",
            "potential_solutions": [
                "Lightweight feature request aggregator with email/Slack/Twitter integrations",
                "AI-powered request deduplication and ranking tool",
                "Simple voting board with multi-channel intake automation"
            ],
            "market_size_estimate": "Large - Every SaaS company needs feature request management, and existing tools are overbuilt for small teams",
            "existing_solutions": ["Canny", "Productboard", "Nolt", "Fider"],
            "opportunity_score": 82,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_002",
            "subreddit": "webdev",
            "title": "Frustrated with managing environment variables across 12 microservices",
            "body": "Our team has 12 microservices and keeping .env files in sync is a nightmare. Someone always forgets to update one service when we add a new variable. We've looked at HashiCorp Vault but it's massive overkill for our 5-person team. Just need something simple that lets us manage shared env vars with inheritance.",
            "author": "devops_pain",
            "url": "https://reddit.com/r/webdev/comments/demo002",
            "score": 234,
            "num_comments": 67,
            "created_utc": time.time() - 86400 * 1,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Managing environment variables across many microservices is painful — existing tools are overkill for small teams",
            "category": "Developer Tools",
            "severity": 5,
            "affected_audience": "Small-to-medium development teams running microservice architectures",
            "potential_solutions": [
                "Lightweight env variable manager with inheritance and sync across services",
                "CLI tool that validates all services have required env vars before deploy",
                "Git-based env management with encryption and team sharing"
            ],
            "market_size_estimate": "Large - Millions of dev teams use microservices, and env management is universally painful",
            "existing_solutions": ["HashiCorp Vault", "Doppler", "1Password Secrets", "AWS Parameter Store"],
            "opportunity_score": 88,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_003",
            "subreddit": "Entrepreneur",
            "title": "Why isn't there a simple tool to track competitor pricing changes?",
            "body": "I run a SaaS and I want to know whenever my competitors change their pricing pages. I've been manually checking 10 competitor sites weekly which is a huge waste of time. Would love something that just monitors pricing pages and alerts me to changes.",
            "author": "competitive_intel",
            "url": "https://reddit.com/r/Entrepreneur/comments/demo003",
            "score": 156,
            "num_comments": 38,
            "created_utc": time.time() - 86400 * 3,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "No simple tool to automatically monitor competitor pricing page changes and get alerts",
            "category": "Business",
            "severity": 3,
            "affected_audience": "SaaS founders and product marketers who need competitive intelligence",
            "potential_solutions": [
                "Pricing page monitoring tool with change detection and email alerts",
                "Competitive intelligence dashboard tracking pricing, features, and positioning",
                "Browser extension that highlights changes on competitor pages since last visit"
            ],
            "market_size_estimate": "Medium - Niche but high willingness to pay among SaaS companies",
            "existing_solutions": ["Visualping", "Kompyte", "Crayon"],
            "opportunity_score": 71,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_004",
            "subreddit": "startups",
            "title": "Tired of manually creating investor update emails every month",
            "body": "Every month I spend 2-3 hours pulling metrics from Stripe, Google Analytics, and our database to create an investor update email. Then I have to format it nicely and send it to 15 different investors. There has to be a better way. I'd pay good money for something that auto-generates these from my data sources.",
            "author": "series_a_ceo",
            "url": "https://reddit.com/r/startups/comments/demo004",
            "score": 312,
            "num_comments": 89,
            "created_utc": time.time() - 86400 * 1.5,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Creating monthly investor update emails is time-consuming — requires manually pulling data from multiple sources and formatting",
            "category": "Business",
            "severity": 4,
            "affected_audience": "Startup founders who report to investors regularly",
            "potential_solutions": [
                "Auto-generated investor updates pulling from Stripe, analytics, and databases",
                "Investor relations platform with template emails and metric dashboards",
                "AI-powered report builder that connects to business tools and drafts updates"
            ],
            "market_size_estimate": "Medium - Tens of thousands of funded startups globally, high willingness to pay",
            "existing_solutions": ["Visible.vc", "Carta Updates", "Cabal"],
            "opportunity_score": 79,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_005",
            "subreddit": "selfhosted",
            "title": "Can't find a good self-hosted alternative to Calendly that actually works",
            "body": "I've tried Cal.com (too complex to self-host), EasyAppointments (outdated UI), and a few others. All I want is a clean scheduling tool I can run on my own server. Something that handles timezone conversion, integrates with my Google Calendar, and doesn't look like it was built in 2005.",
            "author": "privacy_first_dev",
            "url": "https://reddit.com/r/selfhosted/comments/demo005",
            "score": 445,
            "num_comments": 112,
            "created_utc": time.time() - 86400 * 4,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "No good self-hosted scheduling tool exists — existing options are either too complex to deploy or have outdated UIs",
            "category": "Productivity",
            "severity": 4,
            "affected_audience": "Privacy-conscious developers and small businesses who want to self-host their tools",
            "potential_solutions": [
                "Modern, minimal self-hosted scheduling tool with one-click Docker deploy",
                "Lightweight Calendly alternative focused on simplicity and Google Calendar sync",
                "Open-source scheduling widget that can be embedded anywhere"
            ],
            "market_size_estimate": "Large - Self-hosted community is growing rapidly, scheduling is universal need",
            "existing_solutions": ["Cal.com", "EasyAppointments", "Calendso"],
            "opportunity_score": 85,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_006",
            "subreddit": "smallbusiness",
            "title": "I need a simple way to collect testimonials from customers",
            "body": "I ask happy customers for testimonials and they always say yes but then never follow through. I need something dead simple — send them a link, they record a short video or write text, and it shows up on my website. Testimonial.to is $50/mo which is nuts for what it does.",
            "author": "small_biz_sarah",
            "url": "https://reddit.com/r/smallbusiness/comments/demo006",
            "score": 98,
            "num_comments": 31,
            "created_utc": time.time() - 86400 * 5,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Collecting customer testimonials is friction-heavy — customers agree but don't follow through, and existing tools are overpriced",
            "category": "Marketing",
            "severity": 3,
            "affected_audience": "Small business owners and solopreneurs who need social proof for their websites",
            "potential_solutions": [
                "Simple one-link testimonial collector with video/text options and auto website embed",
                "Testimonial follow-up automation — gentle reminders until they submit",
                "AI-assisted testimonial prompts that make it easy for customers to write"
            ],
            "market_size_estimate": "Large - Every business needs testimonials, current solutions are overpriced",
            "existing_solutions": ["Testimonial.to", "Senja", "VideoAsk"],
            "opportunity_score": 68,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_007",
            "subreddit": "programming",
            "title": "Is there a tool that generates API documentation from actual traffic?",
            "body": "Our API docs are always out of date because devs forget to update them. I want something that watches actual API traffic (like a proxy) and auto-generates/updates OpenAPI specs from real requests and responses. Would save us hours of documentation work.",
            "author": "api_doc_hater",
            "url": "https://reddit.com/r/programming/comments/demo007",
            "score": 521,
            "num_comments": 134,
            "created_utc": time.time() - 86400 * 2.5,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "API documentation is always outdated because developers forget to update it manually",
            "category": "Developer Tools",
            "severity": 4,
            "affected_audience": "Backend developers and API teams at companies of all sizes",
            "potential_solutions": [
                "Traffic-based API documentation generator that creates OpenAPI specs from real requests",
                "API proxy that detects schema changes and auto-updates docs",
                "CI/CD integration that validates API docs match actual implementation"
            ],
            "market_size_estimate": "Large - Every company with an API faces this problem",
            "existing_solutions": ["Optic", "Readme.io", "Swagger/OpenAPI generators"],
            "opportunity_score": 91,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_008",
            "subreddit": "productivity",
            "title": "Frustrated: why do all meeting note tools require me to invite a bot?",
            "body": "I've tried Otter, Fireflies, Grain, etc. They all require me to add a bot to the meeting which is awkward with clients. I just want to upload a recording after the meeting and get structured notes. Or even better, use my laptop's mic directly without anyone knowing there's AI involved.",
            "author": "meeting_minimalist",
            "url": "https://reddit.com/r/productivity/comments/demo008",
            "score": 267,
            "num_comments": 72,
            "created_utc": time.time() - 86400 * 1,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Meeting transcription tools are socially awkward — they require visible bots that clients notice and question",
            "category": "Productivity",
            "severity": 4,
            "affected_audience": "Professionals who have client-facing meetings and want discreet note-taking",
            "potential_solutions": [
                "Local-first meeting recorder that captures system audio without a visible bot",
                "Post-meeting upload tool that generates structured notes from any recording",
                "Desktop app that silently transcribes meetings using local AI"
            ],
            "market_size_estimate": "Large - Millions of professionals have meetings daily, privacy concerns are growing",
            "existing_solutions": ["Otter.ai", "Fireflies.ai", "Grain", "tl;dv"],
            "opportunity_score": 86,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_009",
            "subreddit": "indiehackers",
            "title": "Looking for a way to A/B test my landing page without paying $200/mo",
            "body": "Google Optimize shut down, VWO and Optimizely are enterprise-priced. I just want to test two headlines on my landing page. Simple split test, show me which converts better. Why does this need to cost $200/month?",
            "author": "bootstrapper_mike",
            "url": "https://reddit.com/r/indiehackers/comments/demo009",
            "score": 189,
            "num_comments": 56,
            "created_utc": time.time() - 86400 * 6,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Affordable A/B testing tools for indie makers don't exist after Google Optimize shutdown — alternatives are enterprise-priced",
            "category": "Marketing",
            "severity": 3,
            "affected_audience": "Indie hackers, bootstrapped founders, and small marketing teams",
            "potential_solutions": [
                "Simple, affordable A/B testing tool for landing pages ($10-20/mo tier)",
                "Open-source split testing script that works with any static site",
                "Lightweight JS snippet for headline/CTA testing with built-in analytics"
            ],
            "market_size_estimate": "Medium - Large number of indie makers, but low price point means need volume",
            "existing_solutions": ["VWO", "Optimizely", "PostHog (has basic experiments)"],
            "opportunity_score": 64,
        },
    },
    {
        "post": {
            "reddit_id": "t3_demo_010",
            "subreddit": "digitalnomad",
            "title": "Wish there was an app that tells me the best time to schedule calls across timezones",
            "body": "I work with people in 5 different timezones. Every time I need to schedule a call, I'm juggling World Clock apps and mental math. I want something that shows me overlapping work hours for my frequent contacts and suggests optimal meeting times. Bonus if it considers my energy levels / preferences.",
            "author": "nomad_scheduler",
            "url": "https://reddit.com/r/digitalnomad/comments/demo010",
            "score": 145,
            "num_comments": 41,
            "created_utc": time.time() - 86400 * 3,
            "post_type": "submission",
        },
        "analysis": {
            "pain_point_summary": "Scheduling calls across multiple timezones requires too much mental math — no tool optimizes for overlapping work hours",
            "category": "Productivity",
            "severity": 3,
            "affected_audience": "Remote workers, digital nomads, and distributed teams spanning multiple timezones",
            "potential_solutions": [
                "Smart timezone scheduler that learns your contacts' timezones and shows optimal windows",
                "Visual overlap tool showing everyone's work hours with one-click scheduling",
                "Calendar integration that auto-suggests meeting times based on timezone + preference data"
            ],
            "market_size_estimate": "Medium - Growing remote workforce, but timezone tools are a crowded space",
            "existing_solutions": ["World Time Buddy", "Calendly", "Every Time Zone"],
            "opportunity_score": 58,
        },
    },
]


def load_demo_data():
    """Load sample pain points into the database for demo purposes."""
    init_db()

    loaded = 0
    for item in SAMPLE_PAIN_POINTS:
        post_id = insert_post(item["post"])
        if post_id:
            analysis = item["analysis"].copy()
            analysis["raw_llm_response"] = json.dumps(item["analysis"])
            insert_analysis(post_id, analysis)
            loaded += 1

    return loaded


if __name__ == "__main__":
    count = load_demo_data()
    print(f"✅ Loaded {count} sample pain points into the database.")
