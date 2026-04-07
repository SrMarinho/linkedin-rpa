import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from src.config.settings import logger


class IndeedJobsPage:
    def __init__(self, driver: WebDriver, url: str):
        self.driver = driver
        self.url = url

    def get_job_cards(self) -> list[WebElement]:
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
            )
            return self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
        except Exception:
            logger.info("No job cards found on page")
            return []

    def get_job_title(self) -> str:
        try:
            el = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR,
                    "h2.jobTitle, "
                    "h2.jobsearch-JobInfoHeader-title, "
                    "[data-testid='jobsearch-JobInfoHeader-title']",
                )
            )
            return el.text.strip()
        except Exception:
            return ""

    def get_job_description(self) -> str:
        try:
            el = WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.ID, "jobDescriptionText")
            )
            return el.text.strip()
        except Exception:
            return ""

    def get_apply_btn(self) -> WebElement | None:
        # Indeed Apply (native form) — preferred
        try:
            btn = self.driver.find_element(
                By.CSS_SELECTOR,
                "button.indeed-apply-button, [data-testid='indeedApplyButton']",
            )
            if btn.is_displayed() and btn.is_enabled():
                logger.info("Found Indeed Apply button (native)")
                return btn
        except Exception:
            pass

        # Fallback: any visible apply button with known text
        try:
            btn = self.driver.find_element(
                By.XPATH,
                "//button[contains(@class,'indeed-apply') or "
                "contains(normalize-space(),'Candidatar-se facilmente') or "
                "contains(normalize-space(),'Apply now')]",
            )
            if btn.is_displayed() and btn.is_enabled():
                logger.info("Found apply button via text match")
                return btn
        except Exception:
            pass

        logger.info("No Indeed Apply button found (likely external application)")
        return None

    def next_page_url(self, base_url: str, page_num: int) -> str:
        start = (page_num - 1) * 10
        if "start=" in base_url:
            import re
            return re.sub(r"start=\d+", f"start={start}", base_url)
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}start={start}"
