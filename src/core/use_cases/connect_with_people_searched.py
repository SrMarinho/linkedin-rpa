import time
from selenium.webdriver.remote.webdriver import WebDriver
from src.automation.pages.tech_recruiter_search_page import TechRecruiterSeachPage


class ConnectWithPeopleSearched:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.tech_recruiter_search_page = TechRecruiterSeachPage(self.driver)
    
    def run(self):
        time.sleep(2)
        self.tech_recruiter_search_page.navigate()
        time.sleep(5)
        self.tech_recruiter_search_page.get_connectables_list()