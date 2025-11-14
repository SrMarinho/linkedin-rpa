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

    def _get_recruiter_list(self) -> list[WebElement]:
        time.sleep(1)
        try:
            logger.info(f"{self.PAGE_NAME} - Pegando container da lista de recrutadores")
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-view-name='people-search-result']"))
            )
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Erro ao pegar container da lista de recrutadores - {str(e)}"
            )

        print(container.get_attribute("innerHTML"))

        main_sections = WebDriverWait(self.driver, 10).until(
            lambda _: container.find_elements(By.XPATH, "./*")
        )

        if not main_sections[1]:
            return []

        return WebDriverWait(self.driver, 10).until(
            lambda _: main_sections[1].find_element(By.TAG_NAME, "ul")
        )

    def get_connectables_list(self) -> list[WebElement]:
        try:
            logger.info(f"{self.PAGE_NAME} - Pegando lista de recrutadores")
            recruiters_list = self._get_recruiter_list()
            return []

            recruiters = WebDriverWait(self.driver, 10).until(
                lambda _: recruiters_list.find_elements(By.TAG_NAME, "li")
            )

            return recruiters
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Erro ao pegar lista de recrutadores - {str(e)}"
            )
            return []

    def try_connect(self, recruiter: WebElement):
        try:
            time.sleep(0.5)
            btn = WebDriverWait(recruiter, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "artdeco-button__text"))
            )

            if btn.text != "Conectar":
                return False

            btn.click()
            logger.info(f"{self.PAGE_NAME} - Clicando em conectar")
            time.sleep(2)
            self._try_connect_confirmation()
            return True
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Erro ao tentar conectar com recrutador - {str(e)}"
            )
            return False

    def _try_connect_confirmation(self):
        try:
            logger.info(f"{self.PAGE_NAME} - Confirmando conexão")
            modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "artdeco-modal-outlet")
                )  # Usando EC corretamente
            )
            logger.debug(modal.get_attribute("innerHTML"))

            btn_enviar_sem_nota = WebDriverWait(modal, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CLASS_NAME,
                        "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1",
                    )
                )
            )

            logger.debug(btn_enviar_sem_nota)
            # btn_enviar_sem_nota.click()

            # buttons = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1"))
            # )
            return True
        except Exception as e:
            logger.error(
                f"{self.PAGE_NAME} - Erro ao tentar confirmar conexão com recrutador - {str(e)}"
            )
            raise e
            return False
