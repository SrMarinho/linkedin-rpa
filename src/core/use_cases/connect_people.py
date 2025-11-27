from src.automation.pages.tech_recruiter_search_page import TechRecruiterSearchPage


class ConnectPeople:
    def __init__(self, tech_recruiter_search_page: TechRecruiterSearchPage):
        self.page = tech_recruiter_search_page
        self.invite_sended = 0

    def _connect_with_all_recruiters(self):
        while btn_connect := self.page.get_btn_connect():
            if not btn_connect:
                break

            btn_connect.click()
            self.page.confirm_invitation()
            self.invite_sended += 1

    def run(self):
        while btn_connect := self.page.get_btn_connect():
            if not btn_connect:
                break

            btn_connect.click()
            self.page.confirm_invitation()
            self.invite_sended += 1