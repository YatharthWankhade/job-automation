<h1 align="center">🤖 Job Application Automation</h1>

<p align="center">
  <em>Apply smarter, not harder. AI-powered job hunting on autopilot.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-AI%20Powered-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Playwright-Browser%20Automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

---

## What It Does

This system automates your entire job search workflow — from finding relevant openings to sending follow-up emails — so you can focus on preparing for interviews instead of scrolling job boards.

```
Scrape Jobs → Match with Resume (AI) → Generate Cover Letter → Apply → Follow-up
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Multi-Platform Scraping** | LinkedIn, Indeed, and more — all in one run |
| � **AI Resume Matching** | Google Gemini scores each job 0–100% against your resume |
| 📝 **Auto Cover Letters** | Personalized letters generated per job, per company |
| ✅ **Dual Application Modes** | Auto-apply (85%+) or review queue (70–84%) |
| 📧 **Smart Follow-ups** | Scheduled follow-up emails every 2 days |
| 🚫 **Zero Duplicates** | Never applies to the same job twice |
| 🧪 **Dry-Run Mode** | Test the full pipeline without sending anything |
| 📊 **Tracking Dashboard** | SQLite DB records every job, application, and follow-up |

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/job-automation.git
cd job-automation
./setup.sh   # Creates venv, installs deps, installs Playwright
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your keys:
#   GEMINI_API_KEY=your_key_here
#   GMAIL_APP_PASSWORD=your_app_password  (optional, for follow-ups)
```

### 3. Add Your Resume

Edit `resume_data.json` with your actual info — skills, experience, education, and job preferences. This is what the AI uses to match and score jobs.

### 4. Customize Search

Edit `config.yaml` to set your target roles, locations, and platforms:

```yaml
search:
  keywords: ["software engineer", "backend developer"]
  locations: ["Remote", "New York"]

matching:
  threshold: 70  # Only consider jobs with 70%+ match

application:
  mode: "both"   # auto for 85%+, review queue for 70-84%
```

### 5. Run It

```bash
# Safe first run — dry mode, no actual applications
python main.py run-all --limit 5 --dry-run

# When ready, go live
python main.py run-all --limit 20
```

---

## 🛠 CLI Reference

```bash
python main.py scrape      # Scrape new job listings
python main.py match       # AI-match scraped jobs with your resume
python main.py review      # View jobs in your review queue
python main.py apply       # Submit applications
python main.py followup    # Send scheduled follow-up emails
python main.py stats       # View overall statistics

# Common flags
  --limit N       Max items to process
  --dry-run       Preview without submitting/sending
  --mode auto     Force auto-apply mode
```

---

## 🗂 Project Structure

```
job-automation/
├── main.py                   # CLI entrypoint & orchestrator
├── config.yaml               # All configuration in one place
├── resume_data.json          # Your structured resume data
├── setup.sh                  # One-command setup script
│
├── scrapers/
│   ├── base_scraper.py       # Shared scraping utilities
│   ├── linkedin_scraper.py   # LinkedIn (Playwright-based)
│   └── indeed_scraper.py     # Indeed (BeautifulSoup-based)
│
├── matcher/
│   ├── resume_parser.py      # Parses PDF / DOCX / TXT / JSON
│   └── job_matcher.py        # AI scoring & routing logic
│
├── applicator/
│   └── base_applicator.py    # Application submission engine
│
├── followup/
│   ├── email_manager.py      # Gmail / SMTP integration
│   └── scheduler.py          # Follow-up timing & dispatch
│
└── utils/
    ├── database.py            # SQLite schema & queries
    ├── ai_helper.py           # Gemini API wrapper
    └── logger.py              # Coloured console + file logging
```

---

## 🧠 How the AI Matching Works

Each scraped job is sent to **Google Gemini** along with your resume data. Gemini returns:

- **Match score** (0–100%)
- **Rationale** for the score
- **Missing skills** — so you know what to highlight

Jobs are then routed:

```
≥ 85%  →  Auto-apply queue
70–84% →  Review queue (your approval needed)
< 70%  →  Skipped
```

---

## 🔒 Safety First

Before going live, always:

```bash
# 1. Run dry-run to preview everything
python main.py run-all --limit 3 --dry-run

# 2. Check match quality
python main.py review

# 3. Inspect generated cover letters in the logs
tail -f logs/job_automation.log

# 4. Start small on first real run
python main.py apply --limit 1
```

---

## 🔧 Extending the System

### Add a New Job Platform

```python
# scrapers/glassdoor_scraper.py
from scrapers.base_scraper import BaseScraper

class GlassdoorScraper(BaseScraper):
    def get_platform_name(self): return "glassdoor"
    def search_jobs(self, keywords, locations, **kwargs): ...
    def get_job_details(self, url): ...
```

Then add `"glassdoor"` to `platforms.enabled` in `config.yaml`.

---

## 📋 Prerequisites

- Python 3.8+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (free tier works)
- A Gmail App Password *(optional — only needed for follow-up emails)*

---

## ⚠️ Current Limitations

- Application **submission** runs in demonstration/dry-run mode by default (production browser automation can be enabled)
- LinkedIn scraping requires a **one-time manual login** — session is saved after that
- Always respect each platform's Terms of Service

---

## 📄 License

MIT — use freely, contribute back if you improve it.

---

<p align="center">
  Built with 🤖 Google Gemini · 🎭 Playwright · 🐍 Python
</p>
