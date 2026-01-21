import os
import src.config.settings as setting
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.automation.tasks.connection_manager import ConnectionManager
from src.config.settings import logger
from dotenv import load_dotenv


def setup_chrome_options(headless: bool = False):
    user_profile = os.environ["USERPROFILE"]
    chrome_user_data = f"{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data"

    options = Options()
    options.add_argument(f"user-data-dir={chrome_user_data}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    return options


def get_config() -> dict:
    env_headless = str(os.getenv("HEADLESS")).upper()
    headless = False if env_headless == "FALSE" else True

    return {"headless": headless}


def setup():
    config = get_config()
    options = setup_chrome_options(**config)
    driver = webdriver.Chrome(options=options)
    return driver


def main():
    with setup() as driver:
        try:
            ConnectionManager(driver).run()
            driver.save_screenshot(f"{setting.screenshots_path}.png")
        except Exception as e:
            logger.critical(f"{str(e)}")
            driver.save_screenshot(f"{setting.screenshots_path}.png")
            raise


if __name__ == "__main__":
    load_dotenv()
    main()
