# JobPilot

Automated job application bot with AI-powered evaluation. Currently supports LinkedIn (Easy Apply + connection requests), with an architecture designed to add new job boards.

## Features

- **Apply**: Evaluates jobs against your resume and applies automatically
  - Filters by language (pt-BR only by default)
  - Filters by seniority level
  - Estimates salary expectation based on job and market data
  - Answers custom form questions using AI
  - Tracks applied jobs to avoid duplicates
- **Connect**: Sends connection requests automatically (LinkedIn)
- **Bot**: Control JobPilot remotely via Telegram — start/stop tasks, check status, and receive notifications for every application sent

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Google Chrome
- Account already logged in on Chrome
- Claude Code with Pro plan (used by the AI evaluator)

## Installation

```bash
git clone https://github.com/SrMarinho/jobpilot.git
cd jobpilot
uv sync
```

## Configuration

Create a `.env` file at the project root:

```env
HEADLESS=FALSE

# Telegram (optional — required for bot mode and notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_channel_id   # channel/group for notifications
TELEGRAM_ADMIN_ID=your_personal_id # your personal chat ID for commands
```

> Set `HEADLESS=TRUE` to run Chrome in the background (no visible window).

To get your `TELEGRAM_ADMIN_ID`, send any message to your bot and open:
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```
Your `chat.id` will appear in the response.

## Login

Before running any task, log in to LinkedIn (or other supported sites) once so the session is saved to the browser profile:

```bash
uv run main.py login linkedin
```

A browser window will open. Log in normally, then close it. The session is persisted in `bot_profile/` and reused on every subsequent run.

## Usage

> **Tip:** The first time you run `connect` or `apply`, you must pass `--url`. After that, the URL is saved locally in `files/last_urls.json` and you can omit it in future runs.

---

### Apply to jobs

```bash
# First run — URL required
uv run main.py apply --url "JOB_SEARCH_URL" --resume "path/to/resume.pdf"

# Subsequent runs — reuses last saved URL
uv run main.py apply
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--url` | First run only | Job search URL (LinkedIn: enable Easy Apply filter with `f_AL=true`) |
| `--resume` | No | Path to resume PDF or TXT (default: `resume.txt`) |
| `--preferences` | No | Preferences to guide evaluation (e.g. `'prefer backend, Python, remote'`) |
| `--level` | No | Seniority level filter: `junior`, `pleno`, `senior` |
| `--max-pages` | No | Max pages to process (default: 100) |

**Example (LinkedIn):**
```bash
uv run main.py apply \
  --url "https://www.linkedin.com/jobs/search/?keywords=python+developer&f_AL=true" \
  --resume "resume.pdf" \
  --preferences "prefer backend, Python, remote" \
  --level junior
```

---

### Send connection requests (LinkedIn)

```bash
# First run — URL required
uv run main.py connect --url "PEOPLE_SEARCH_URL"

# Subsequent runs — reuses last saved URL
uv run main.py connect

# Resume from the last page where it stopped
uv run main.py connect --continue
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--url` | First run only | LinkedIn people search URL |
| `--start-page` | No | Page to start from (default: 1) |
| `--max-pages` | No | Max pages to process (default: 100) |
| `--continue` | No | Resume from the last page where the previous run stopped |

> The current page is saved in real time as the bot runs. If execution is interrupted, `--continue` picks up exactly where it left off.

---

### Telegram Bot

Start the bot to control JobPilot remotely via Telegram:

```bash
uv run main.py bot
```

| Command | Description |
|---------|-------------|
| `/connect` | Start sending connection requests (bot will ask for the URL) |
| `/apply <url>` | Start applying to jobs |
| `/status` | Check if a task is running |
| `/stop` | Stop the current task |
| `/resume` | Upload a new resume file (PDF or TXT) |
| `/ping` | Check if the bot is alive |
| `/reiniciar` | Restart the bot process |
| `/help` | List all commands |

The bot sends a Telegram notification to your channel every time an application is submitted.

---

## How the apply flow works

```
For each job found:
  1. Check if already applied (applied_jobs.json)
  2. AI evaluates:
     - Job language (pt-BR only by default)
     - Seniority level match (if --level provided)
     - Technical fit with resume
     - Alignment with preferences
  3. If approved:
     - Estimate salary expectation
     - Click apply button
     - Fill form fields (salary, custom questions via AI)
     - Submit
     - Save to applied_jobs.json
```

## Local files generated

| File | Description |
|------|-------------|
| `applied_jobs.json` | Record of all submitted applications |
| `files/last_urls.json` | Last URL and page saved per task (`connect`, `apply`) |
| `screenshots.png` | Screenshot taken at the end of execution |

> These files are in `.gitignore` and are not committed to the repository.

## Project structure

```
jobpilot/
├── main.py                                   # Entry point and CLI
└── src/
    ├── automation/
    │   ├── pages/                            # Site-specific page objects
    │   │   ├── people_search_page.py         # LinkedIn people search
    │   │   └── jobs_search_page.py           # LinkedIn jobs search
    │   └── tasks/                            # Orchestration layer
    │       ├── connection_manager.py
    │       └── job_application_manager.py
    ├── bot/
    │   └── telegram_bot.py                   # Telegram bot (polling + command handling)
    ├── core/
    │   └── use_cases/                        # Site-agnostic business logic
    │       ├── job_evaluator.py              # AI job evaluation
    │       ├── salary_estimator.py           # AI salary estimation
    │       ├── job_application_handler.py    # Form filling and submission
    │       └── applied_jobs_tracker.py       # Persistence layer
    └── utils/
        └── telegram.py                       # Telegram notification helper
```

### Adding a new job board

1. Create a new page object under `src/automation/pages/` implementing the same interface as `JobsSearchPage`
2. Instantiate it in `JobApplicationManager` based on the URL domain
3. The core use cases (`JobEvaluator`, `SalaryEstimator`, etc.) work unchanged
