from selenium.webdriver.remote.webdriver import WebDriver
from src.automation.pages.tech_recruiter_search_page import TechRecruiterSeachPage
from src.config.settings import logger


class ConnectWithPeopleSearched:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.tech_recruiter_search_page = TechRecruiterSeachPage(self.driver)
        self.invite_sended = 0

    def _connect_with_all_recruiters(self):
        while btn_connect := self.tech_recruiter_search_page.get_btn_connect():
            if not btn_connect:
                break

            btn_connect.click()
            self.tech_recruiter_search_page.confirm_invitation()
            self.invite_sended += 1

    def run(self):
        self.tech_recruiter_search_page.navigate()

        while True:
            self._connect_with_all_recruiters()
            next_page = self.tech_recruiter_search_page.btn_next_page()
            if not next_page:
                break
            next_page.click()
        logger.info(f"Número de pessoas conectadas: {self.invite_sended}")
