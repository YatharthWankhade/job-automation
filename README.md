# Job Application Automation System

An intelligent job application automation system that scrapes job postings, matches them with your resume using AI, applies automatically, and sends follow-up emails.

## Features

- 🔍 **Multi-Platform Job Scraping**: Scrapes jobs from LinkedIn, Indeed, and other platforms
- 🤖 **AI-Powered Matching**: Uses Google Gemini to match jobs with your resume (70% threshold)
- 📝 **Auto-Generated Cover Letters**: Creates personalized cover letters for each application
- ✅ **Dual Application Modes**: 
  - Auto-apply for 85%+ matches
  - Review queue for 70-84% matches
- 📧 **Automated Follow-ups**: Sends follow-up emails every 2 days
- 🚫 **Duplicate Prevention**: Never applies to the same job twice
- 📊 **Progress Tracking**: SQLite database tracks all jobs, applications, and follow-ups

## Prerequisites

- Python 3.8+
- Google Gemini API key
- (Optional) Gmail account for sending follow-ups

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /Users/yatharthwankhade/Developer/job-automation
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (for LinkedIn scraping):
   ```bash
   playwright install chromium
   ```

5. **Set up environment variables**:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   # Optional: for email follow-ups
   export GMAIL_APP_PASSWORD="your-gmail-app-password"
   ```

## Configuration

Edit `config.yaml` to customize:

- **Job search criteria**: Keywords, locations, experience levels
- **Platforms**: Enable/disable LinkedIn, Indeed, etc.
- **Matching threshold**: Default is 70%
- **Application mode**: `auto`, `review_queue`, or `both`
- **Follow-up schedule**: Default is every 2 days
- **Rate limiting**: Prevent being flagged as a bot

## Resume Setup

1. **Edit `resume_data.json`** with your information:
   - Personal info (name, email, phone, LinkedIn, GitHub)
   - Skills (programming languages, frameworks, tools)
   - Experience (companies, positions, achievements)
   - Education and certifications
   - Preferences (desired roles, industries, remote preference)

2. **(Optional) Add your resume file**:
   - Place your resume PDF/DOCX in the project directory
   - Update `config.yaml` with the filename

## Usage

### Run Full Pipeline (Recommended for First Time)

```bash
# Dry run (doesn't actually apply or send emails)
python main.py run-all --limit 5 --dry-run
```

### Individual Commands

**1. Scrape Jobs**:
```bash
python main.py scrape --limit 50
```

**2. Match Jobs with Resume**:
```bash
python main.py match
```

**3. Review Matched Jobs**:
```bash
python main.py review
```

**4. Apply to Jobs**:
```bash
# Dry run first
python main.py apply --limit 5 --dry-run

# Actual application (when ready)
python main.py apply --limit 5
```

**5. Send Follow-ups**:
```bash
# Dry run first
python main.py followup --dry-run

# Actual sending (when ready)
python main.py followup
```

**6. View Statistics**:
```bash
python main.py stats
```

## How It Works

### 1. Job Scraping
- Searches configured platforms (LinkedIn, Indeed) for jobs matching your criteria
- Extracts job title, company, location, description, requirements
- Stores in SQLite database with duplicate detection

### 2. AI Matching
- Uses Google Gemini to analyze each job description
- Compares with your resume data
- Generates match score (0-100%) and rationale
- Identifies missing skills

### 3. Application Routing
- **85%+ match**: Auto-apply (if mode is `both` or `auto`)
- **70-84% match**: Add to review queue
- **<70% match**: Rejected, not applied

### 4. Cover Letter Generation
- AI generates personalized cover letter for each job
- Highlights relevant experience and skills
- Tailored to company and role

### 5. Application Submission
- **(Current version)**: Dry-run mode shows what would be submitted
- **(Production version)**: Would use browser automation to fill forms and submit

### 6. Follow-up Scheduling
- Automatically schedules follow-ups for applied jobs
- Default: Day 2, Day 4, Day 7 after application
- AI-generated personalized follow-up emails

## Database Schema

The system uses SQLite with three main tables:

- **jobs**: All scraped job postings
- **applications**: Application records with match scores and status
- **followups**: Scheduled and sent follow-up emails

## Safety Features

- **Dry-run mode**: Test everything before actual submission
- **Rate limiting**: Delays between requests to avoid detection
- **Duplicate prevention**: Checks database before applying
- **Application limits**: Configure max applications per day
- **Review queue**: Manual approval option for borderline matches

## Troubleshooting

### LinkedIn Login Required
- The LinkedIn scraper will open a browser window
- Log in manually when prompted
- Session will be saved for future runs

### API Rate Limits
- Gemini API has rate limits - adjust delays in config
- Use `--limit` flag to process fewer jobs at once

### Missing Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

## Customization

### Add More Job Platforms

1. Create a new scraper in `scrapers/` (e.g., `glassdoor_scraper.py`)
2. Inherit from `BaseScraper`
3. Implement `search_jobs()` and `get_job_details()`
4. Add to `config.yaml` platforms list

### Customize Matching Logic

Edit `matcher/job_matcher.py` to adjust:
- Matching algorithm
- Threshold calculations
- Skill weighting

### Customize Email Templates

Edit `followup/scheduler.py` to modify:
- Follow-up timing
- Email generation prompts
- Signature format

## Important Notes

⚠️ **Current Limitations**:
- Application submission is in dry-run/demonstration mode
- Email sending shows preview but doesn't actually send (unless SMTP configured)
- LinkedIn scraping requires manual login

⚠️ **Before Going Live**:
1. Test thoroughly with `--dry-run` flag
2. Review generated cover letters for quality
3. Start with small `--limit` values
4. Monitor for any platform blocks or rate limits
5. Ensure resume data is accurate and complete

## License

This is a personal automation tool. Use responsibly and in accordance with job platform terms of service.

## Support

For issues or questions:
1. Check the logs in `logs/job_automation.log`
2. Review the configuration in `config.yaml`
3. Ensure all environment variables are set
4. Try with `--dry-run` flag first
