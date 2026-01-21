from src.automation.pages.linkedin_search_page import RecruiterSearchPage


class ConnectionHandler:
    def __init__(self, tech_recruiter_search_page: RecruiterSearchPage):
        self.page = tech_recruiter_search_page
        self.invite_sended = 0
        self.last_btn_connect = None

    def run(self):
        while btn_connect := self.page.get_btn_connect():
            if not btn_connect:
                break
            if btn_connect == self.last_btn_connect:
                break

            btn_connect.click()

            btn_confirm = self.page.btn_confirm_invitation()
            if not btn_confirm:
                self.page.close_modal()
                continue
            btn_confirm.click()
            self.invite_sended += 1