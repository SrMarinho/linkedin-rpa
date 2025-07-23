import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config.settings import logger

class TechRecruiterSeachPage:
    URL = "https://www.linkedin.com/search/results/people/?keywords=tech%20recruiter&network=%5B%22S%22%5D&sid=fpd"
    PAGE_NAME = "Tech Recruiter Seach Page"
    
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate(self) -> bool:
        try:
            self.driver.get(self.URL)
            time.sleep(5)
            return True
        except Exception as e:
            logger.info(f"{self.PAGE_NAME} - Não foi possível navegar para a página solicitada - {str(e)}")
            return False
    
    def get_connectables_list(self):
        try:
            container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
            )
            
            recruiters_list = WebDriverWait(self.driver, 10).until(
                lambda _ : container.find_element(By.TAG_NAME, "ul")
            )

            recruiters = WebDriverWait(self.driver, 10).until(
                lambda _ : recruiters_list.find_elements(By.TAG_NAME, "li")
            )

            logger.debug(recruiters.get_property("innerHTML"))
            logger.debug("Recrutadores achados")

            for i, recruiter in enumerate(recruiters):
                # logger.debug(recruiter.get_property("innerHTML"))
                logger.debug(recruiter.get_property("outterHTML"))
        except Exception as e:
            logger.info(f"{self.PAGE_NAME} - Pegar lista de recrutadores - {str(e)}")
            return False