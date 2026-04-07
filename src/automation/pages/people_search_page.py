import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from src.config.settings import logger


class PeopleSearchPage:
    def __init__(self, driver: WebDriver, url: str):
        self.driver = driver
        self.url = url

    def is_invite_limit_reached(self) -> bool:
        try:
            self.driver.find_element(By.CSS_SELECTOR, "[data-test-modal-id='fuse-limit-alert']")
            return True
        except Exception:
            return False

    def close_modal(self) -> None:
        try:
            btn: WebElement = WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "button[aria-label='Fechar']")
            )
            btn.click()
        except Exception:
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            except Exception:
                logger.error("No modal to close")

    def get_confirm_invitation_btn(self) -> WebElement | None:
        logger.info("Waiting for invitation modal")
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "[data-test-modal-container]")
            )
        except Exception:
            logger.error("No modal appeared after clicking Connect")
            return None

        try:
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Retirar convite']")
            logger.info("'Withdraw invite' modal detected, skipping")
            return None
        except Exception:
            pass

        try:
            btn: WebElement = self.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Enviar sem nota']"
            )
            if btn.get_attribute("disabled"):
                logger.info("'Send without note' button is disabled")
                return None
            return btn
        except Exception as e:
            logger.error(f"'Send without note' button not found. {e}")
        return None

    def get_connect_btn(self) -> WebElement | None:
        time.sleep(0.2)
        try:
            logger.info("No target found yet, continuing...")
            btn = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(
                    By.XPATH,
                    "//button[contains(@aria-label,'Convidar') and contains(@aria-label,'conectar')]",
                )
            )
            time.sleep(0.2)
            return btn
        except Exception:
            logger.info("No connect buttons found on page")
        return None
