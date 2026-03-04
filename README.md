# Job Application Automation

> AI-powered job hunting — from scraping to follow-ups, fully automated.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-4285F4?style=flat-square&logo=google&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Overview

This tool automates the full job application lifecycle:

**Scrape → Match → Apply → Follow-up**

It scrapes job listings, uses Google Gemini to match them against your resume, generates tailored cover letters, submits applications, and schedules follow-up emails — all configurable and safe to test with dry-run mode.

---

## Features

- **Multi-platform scraping** — LinkedIn, Indeed, and extensible to others
- **AI resume matching** — Gemini scores each job (0–100%) and explains why
- **Dual application routing** — auto-apply at 85%+, review queue at 70–84%
- **Personalized cover letters** — generated per job, per company
- **Automated follow-ups** — scheduled emails every 2 days
- **Duplicate prevention** — never applies to the same job twice
- **Full observability** — SQLite tracks jobs, applications, and follow-ups
- **Dry-run mode** — preview everything before going live

---

## Getting Started

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/job-automation.git
cd job-automation
./setup.sh
```

### 2. Configure

```bash
cp .env.example .env
# Add your GEMINI_API_KEY (and optionally GMAIL_APP_PASSWORD)
```

Edit `resume_data.json` with your skills, experience, and job preferences.  
Edit `config.yaml` to set target roles, locations, and matching thresholds.

### 3. Run

```bash
# Safe first run — no applications sent
python main.py run-all --limit 5 --dry-run

# Go live when ready
python main.py run-all --limit 20
```

---

## CLI Reference

| Command | Description |
|---|---|
| `scrape` | Scrape new job listings from configured platforms |
| `match` | Score scraped jobs against your resume using AI |
| `review` | View jobs in your approval queue (70–84% match) |
| `apply` | Submit applications |
| `followup` | Send scheduled follow-up emails |
| `stats` | View application statistics |
| `run-all` | Run the full pipeline end-to-end |

**Common flags:** `--limit N` · `--dry-run` · `--mode auto`

---

## How Matching Works

Every job is sent to Gemini with your resume. It returns a **match score**, a **rationale**, and any **skill gaps**.

| Score | Action |
|---|---|
| ≥ 85% | Auto-apply |
| 70–84% | Added to review queue |
| < 70% | Skipped |

---

## Project Structure

```
job-automation/
├── main.py                  # CLI & orchestrator
├── config.yaml              # Configuration
├── resume_data.json         # Your resume (structured)
│
├── scrapers/
│   ├── base_scraper.py
│   ├── linkedin_scraper.py  # Playwright-based
│   └── indeed_scraper.py    # BeautifulSoup-based
│
├── matcher/
│   ├── resume_parser.py     # PDF / DOCX / TXT / JSON
│   └── job_matcher.py       # AI scoring & routing
│
├── applicator/
│   └── base_applicator.py  # Application engine
│
├── followup/
│   ├── email_manager.py     # Gmail / SMTP
│   └── scheduler.py        # Scheduling & dispatch
│
└── utils/
    ├── database.py          # SQLite schema & ops
    ├── ai_helper.py         # Gemini API wrapper
    └── logger.py            # Logging
```

---

## Extending

**Add a new platform** — create a scraper in `scrapers/` inheriting `BaseScraper`, implement `search_jobs()` and `get_job_details()`, then add the platform name to `config.yaml`.

**Adjust matching** — edit thresholds and prompts in `matcher/job_matcher.py` and `utils/ai_helper.py`.

**Custom follow-up templates** — update prompts in `followup/scheduler.py`.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.8+ | |
| Gemini API key | [Get one free](https://aistudio.google.com/app/apikey) |
| Gmail App Password | Optional — only for follow-up emails |

---

## Notes

- LinkedIn scraping requires a one-time manual login; the session is saved afterward
- Application submission defaults to dry-run mode — browser automation must be explicitly enabled
- Always use `--dry-run` before your first live run
- Respect each platform's Terms of Service

---

## License

MIT
