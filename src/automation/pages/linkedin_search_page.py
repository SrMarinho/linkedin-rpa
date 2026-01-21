import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from src.config.settings import logger


class RecruiterSearchPage:
    URL = "https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&network=%5B%22S%22%5D&sid=fpd"
    PAGE_NAME = "Tech Recruiter Search Page"

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate(self) -> bool:
        logger.info(f"{self.PAGE_NAME} - Navegando para a página")
        try:
            self.driver.get(self.URL)
            return True
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Não foi possível navegar para a página solicitada - {str(e)}"
            )
            return False

    def close_modal(self) -> WebElement | None:
        try:
            logger.info(f"{self.PAGE_NAME} - Procurando botão para fechar modal")
            interop_outlet = self.driver.find_element(By.ID, "interop-outlet")
            shadow_root = interop_outlet.shadow_root
            btn: WebElement = WebDriverWait(self.driver, 10).until(
                lambda _: shadow_root.find_element(
                    By.CSS_SELECTOR, "[aria-label='Fechar']"
                )
            )

            btn.click()
        except Exception:
            logger.error(f"{self.PAGE_NAME} - Sem modal para fechar")
        return None

    def btn_confirm_invitation(self) -> WebElement | None:
        logger.info(f"{self.PAGE_NAME} - Clicando em 'Enviar sem nota'")
        try:
            interop_outlet = self.driver.find_element(By.ID, "interop-outlet")
            shadow_root = interop_outlet.shadow_root
            btn: WebElement = WebDriverWait(self.driver, 10).until(
                lambda _: shadow_root.find_element(
                    By.CSS_SELECTOR, "[aria-label='Enviar sem nota']"
                )
            )

            if btn.get_attribute("disabled"):
                logger.info(f"{self.PAGE_NAME} - Botão 'Enviar sem nota' desabilitado")
                return None

            return btn
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Erro ao clicar no botão 'Enviar sem nota'. {e}"
            )
        return None

    def get_btn_connect(self) -> WebElement | None:
        time.sleep(0.2)
        try:
            logger.info(f"{self.PAGE_NAME} - Procurando botão para conectar")
            btn_connect = WebDriverWait(self.driver, 10).until(
                lambda _: self.driver.find_element(
                    By.XPATH, "//span[contains(.,'Conectar')]"
                )
            )
            time.sleep(0.2)
            return btn_connect
        except Exception:
            logger.error(f"{self.PAGE_NAME} - Sem recrutadores para conectar")
        return None

    def btn_next_page(self) -> WebElement | None:
        try:
            logger.info(f"{self.PAGE_NAME} - Buscando botão para próxima página")
            btn_connect = WebDriverWait(self.driver, 5).until(
                lambda _: self.driver.find_element(
                    By.XPATH, "//span[contains(.,'Próxima')]"
                )
            )
            return btn_connect
        except Exception:
            logger.error(f"{self.PAGE_NAME} - Sem próxima página")
        return None
