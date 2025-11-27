import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.automation.tasks.connect_with_searched import ConnectWithSearched
from src.config.settings import logger
from dotenv import load_dotenv


def setup_chrome_options(headless: bool = False):
    user_profile = os.environ["USERPROFILE"]
    chrome_user_data = f"{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data"

    options = Options()
    options.add_argument(f"user-data-dir={chrome_user_data}")
    options.add_argument("profile-directory=Default")
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
    try:
        with setup() as driver:
            ConnectWithSearched(driver).run()
    except Exception as e:
        logger.critical(f"{str(e)}")
        raise


if __name__ == "__main__":
    load_dotenv()
    main()
