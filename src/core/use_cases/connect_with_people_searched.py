import time
from selenium.webdriver.remote.webdriver import WebDriver
from src.automation.pages.tech_recruiter_search_page import TechRecruiterSeachPage
from src.config.settings import logger


class ConnectWithPeopleSearched:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.tech_recruiter_search_page = TechRecruiterSeachPage(self.driver)
    
    def run(self):
        time.sleep(2)
        self.tech_recruiter_search_page.navigate()
        time.sleep(5)
        
        recruiters = self.tech_recruiter_search_page.get_connectables_list()

        for recruiter in recruiters:
            self.tech_recruiter_search_page.try_connect(recruiter)

        return
        while True:
            recruiters = self.tech_recruiter_search_page.get_connectables_list()

            has_connectable = False
            for recruiter in recruiters:
                if self.tech_recruiter_search_page.try_connect(recruiter):
                    break

            if not has_connectable:
                break
