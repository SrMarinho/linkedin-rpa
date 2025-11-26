import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from src.config.settings import logger


class TechRecruiterSeachPage:
    URL = "https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&network=%5B%22S%22%5D&sid=fpd"
    PAGE_NAME = "Tech Recruiter Seach Page"

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate(self) -> bool:
        logger.info(f"{self.PAGE_NAME} - Navegando para a página")
        try:
            self.driver.get(self.URL)
            time.sleep(5)
            return True
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Não foi possível navegar para a página solicitada - {str(e)}"
            )
            return False
    
    
    def confirm_invitation(self) -> None:
        logger.info(f"{self.PAGE_NAME} - Clicando em 'Enviar sem nota'")
        try:
            interop_outlet = self.driver.find_element(By.ID, "interop-outlet")
            shadow_root = interop_outlet.shadow_root
            btn: WebElement = WebDriverWait(self.driver, 10).until(
                lambda _: shadow_root.find_element(By.CSS_SELECTOR, "[aria-label='Enviar sem nota']")
            )

            btn.click()
        except Exception as e:
            logger.error(f"{self.PAGE_NAME} - Erro ao clicar no botão 'Enviar sem nota'. {e}")

    def get_btn_connect(self) -> WebElement | None:
        time.sleep(1)
        try:
            logger.info(f"{self.PAGE_NAME} - Procurando botão para conectar")
            btn_connect = WebDriverWait(self.driver, 10).until(
                lambda _: self.driver.find_element(By.XPATH, "//span[contains(.,'Conectar')]")
            )
            return btn_connect
        except Exception:
            logger.error(
                f"{self.PAGE_NAME} - Sem recrutadores para conectar"
            )
        return None
    
    def btn_next_page(self) -> WebElement | None:
        try:
            logger.info(f"{self.PAGE_NAME} - Buscando botão para próxima página")
            btn_connect = WebDriverWait(self.driver, 10).until(
                lambda _: self.driver.find_element(By.XPATH, "//span[contains(.,'Próxima')]")
            )
            return btn_connect
        except Exception:
            logger.error(
                f"{self.PAGE_NAME} - Sem próxima página"
            )
        return None