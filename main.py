import os
import json
import time
import argparse
import src.config.settings as setting
import undetected_chromedriver as uc
from src.automation.tasks.connection_manager import ConnectionManager
from src.automation.tasks.job_application_manager import JobApplicationManager
from src.config.settings import logger
from dotenv import load_dotenv


BOT_PROFILE_DIR = os.path.join(os.path.dirname(__file__), "bot_profile")
LAST_URLS_FILE = os.path.join(os.path.dirname(__file__), "files", "last_urls.json")


def load_last_urls() -> dict:
    if os.path.exists(LAST_URLS_FILE):
        with open(LAST_URLS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_last_url(task: str, url: str, page: int = 1):
    urls = load_last_urls()
    urls[task] = {"url": url, "page": page}
    with open(LAST_URLS_FILE, "w") as f:
        json.dump(urls, f, indent=2)


def get_config() -> dict:
    env_headless = str(os.getenv("HEADLESS")).upper()
    headless = False if env_headless == "FALSE" else True
    return {"headless": headless}


def setup() -> uc.Chrome:
    config = get_config()
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={BOT_PROFILE_DIR}")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options, headless=config["headless"], version_main=146)
    return driver


LOGIN_URLS = {
    "linkedin": "https://www.linkedin.com/login",
    "glassdoor": "https://www.glassdoor.com/profile/login_input.htm",
    "indeed": "https://secure.indeed.com/auth",
}


def parse_args():
    parser = argparse.ArgumentParser(description="JobPilot")
    subparsers = parser.add_subparsers(dest="task", required=True)

    login_parser = subparsers.add_parser("login", help="Open browser to log in to a job site")
    login_parser.add_argument(
        "site",
        choices=list(LOGIN_URLS.keys()),
        help="Site to log in to: linkedin, glassdoor, indeed",
    )

    connect_parser = subparsers.add_parser("connect", help="Send connection requests")
    connect_parser.add_argument("--url", type=str, default=None, help="LinkedIn people search URL (uses last saved URL if omitted)")
    connect_parser.add_argument("--start-page", type=int, default=None, help="Page to start from (default: 1)")
    connect_parser.add_argument("--max-pages", type=int, default=100, help="Max pages to process (default: 100)")
    connect_parser.add_argument("--continue", dest="resume", action="store_true", help="Resume from the last page where it stopped")

    apply_parser = subparsers.add_parser("apply", help="Apply to jobs via Easy Apply")
    apply_parser.add_argument("--url", type=str, default=None, help="Job search URL (uses last saved URL if omitted)")
    apply_parser.add_argument("--resume", type=str, default="resume.txt", help="Path to resume file (default: resume.txt)")
    apply_parser.add_argument("--preferences", type=str, default="", help="Job preferences to guide evaluation")
    apply_parser.add_argument("--level", type=str, nargs="+", default=[], help="Accepted seniority levels (e.g. --level junior pleno)")
    apply_parser.add_argument("--max-pages", type=int, default=100, help="Max pages to process (default: 100)")

    bot_parser = subparsers.add_parser("bot", help="Start Telegram bot to control JobPilot remotely")
    bot_parser.add_argument("--resume", type=str, default="resume.txt", help="Path to resume file (default: resume.txt)")

    return parser.parse_args()


def run_login(site: str):
    url = LOGIN_URLS[site]
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={BOT_PROFILE_DIR}")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options, headless=False, version_main=146)
    driver.get(url)
    print(f"Browser opened at {url}")
    print("Log in and close the browser window when done.")
    while True:
        try:
            _ = driver.window_handles
            time.sleep(1)
        except Exception:
            break
    print("Browser closed. Login session saved.")


def main():
    args = parse_args()

    if args.task == "login":
        run_login(args.site)
        return

    if args.task == "bot":
        from src.bot.telegram_bot import TelegramBot
        TelegramBot(driver_factory=setup, resume_path=args.resume).run()
        return

    last_urls = load_last_urls()
    saved = last_urls.get(args.task, {})
    if isinstance(saved, str):
        saved = {"url": saved, "page": 1}

    url = args.url
    start_page = args.start_page if hasattr(args, "start_page") and args.start_page is not None else 1
    resume = getattr(args, "resume", False)

    if url:
        save_last_url(args.task, url, page=1)
    else:
        url = saved.get("url")
        if not url:
            print(f"Error: --url is required for the first '{args.task}' run (no saved URL found).")
            return
        if resume:
            start_page = saved.get("page", 1)
            print(f"Resuming '{args.task}' from page {start_page}: {url}")
        else:
            print(f"Using last saved URL for '{args.task}': {url}")

    def on_page_change(page: int):
        save_last_url(args.task, url, page=page)

    driver = setup()
    try:
        if args.task == "connect":
            ConnectionManager(driver, url=url, max_pages=args.max_pages, start_page=start_page, on_page_change=on_page_change).run()
        elif args.task == "apply":
            JobApplicationManager(driver, url=url, resume_path=args.resume, preferences=args.preferences, level=args.level, max_pages=args.max_pages).run()
        try:
            driver.save_screenshot(f"{setting.screenshots_path}.png")
        except Exception:
            pass
    except Exception as e:
        logger.critical(f"{str(e)}")
        try:
            driver.save_screenshot(f"{setting.screenshots_path}.png")
        except Exception:
            pass
        raise
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    load_dotenv()
    main()
