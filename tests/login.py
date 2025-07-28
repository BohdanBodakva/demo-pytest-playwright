from playwright.sync_api import Page, expect

class Login:
    HEADER_TEXT = "Today – Todoist"

    def __init__(self, page: Page):
        self.page = page

    def perform_login(self, get_config) -> Page:
        self.page.goto(get_config['test_url'])

        self.page.fill('input[autocomplete="email"]', get_config['test_username'])
        self.page.fill('input[autocomplete="current-password"]', get_config['test_password'])
        self.page.click("button[type='submit']")

        expect(self.page).to_have_title(Login.HEADER_TEXT, timeout=15_000)

        return self.page
