from selenium.webdriver.remote.webdriver import WebDriver
from src.core.use_cases import ConnectionHandler
from src.automation.pages import RecruiterSearchPage
from src.config.settings import logger


class ConnectionManager:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.searched_page = RecruiterSearchPage(self.driver)
        self.connect_people = ConnectionHandler(self.searched_page)

    def run(self):
        self.searched_page.navigate()

        while True:
            self.connect_people.run()
            next_page = self.searched_page.btn_next_page()
            if not next_page:
                break
            next_page.click()
        logger.info(f"Número de pessoas conectadas: {self.connect_people.invite_sended}")
