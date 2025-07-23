import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.core.use_cases.connect_with_people_searched import ConnectWithPeopleSearched
from src.config.settings import logger


def setup_chrome_options():
    user_profile = os.environ["USERPROFILE"]
    chrome_user_data = f"{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data"

    options = Options()
    options.add_argument(f"user-data-dir={chrome_user_data}")
    options.add_argument("profile-directory=Default")
    return options

def setup():
    options = setup_chrome_options()
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    try:
        with setup() as driver:
            ConnectWithPeopleSearched(driver).run()
    except Exception as e:
        logger.critical(f"{str(e)}")
        raise

if __name__ == "__main__":
    main()