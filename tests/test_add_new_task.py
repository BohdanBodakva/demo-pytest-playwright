import json
import requests
import pytest
from playwright.sync_api import Browser, expect
from login import Login


class TestAddNewTask:
    logged_page = None
    user_token = None
    TASK_TEXT = "Some New Test Task"
    ONE_TASK_TEXT = "1 task"

    @pytest.fixture(scope="class", autouse=True)
    def setup_logged_page(self, get_config, browser: Browser):
        context = browser.new_context()
        page = context.new_page()

        login = Login(page)
        logged_page = login.perform_login(get_config)

        self.__class__.logged_page = logged_page

        yield
        logged_page.close()

    @pytest.fixture(scope="class")
    def do_cleanup(self, get_config):
        yield
        logged_page = self.__class__.logged_page
        logged_page.wait_for_timeout(2000) # wait for backend response to create tasks

        user_str = logged_page.evaluate("() => localStorage.getItem('User')")
        user_dict = json.loads(user_str)
        user_id = user_dict.get('id', None)
        user_token = user_dict.get('token', None)

        api_url = get_config['api_url']
        headers = {"Authorization": f"Bearer {user_token}"}

        list_items = logged_page.locator(
            "div[data-viewport-type='window'] div[data-testid='virtuoso-item-list'] li")
        list_items_count = list_items.count()

        # Get all create task ids
        get_tasks_utl = f"{api_url}/tasks"
        response = requests.get(get_tasks_utl, headers=headers)
        assert 200 <= response.status_code < 300

        response_json = response.json()
        user_task_ids = [task["id"] for task in response_json["results"] if task["added_by_uid"] == user_id]

        # Send DELETE request for each task
        for task_id in user_task_ids:
            delete_task_url = f"{api_url}/tasks/{task_id}"
            response = requests.delete(delete_task_url, headers=headers)
            assert 200 <= response.status_code < 300

    def test_01_add_new_task_only_text(self, do_cleanup):
        logged_page = self.__class__.logged_page

        # Click "Add task" button
        logged_page.locator("span:text('Add task')").first.click()
        logged_page.locator(
            "p[data-placeholder='Description']"
        ).first.wait_for(state="attached", timeout=1_000)

        # Write task text and create
        logged_page.get_by_role("textbox", name="Task name").fill(self.__class__.TASK_TEXT)
        logged_page.click("button[data-testid='task-editor-submit-button']")

        # Verify task was created
        expect(logged_page.locator(
            'div[class="task_content"]', has_text=self.__class__.TASK_TEXT).first
        ).to_be_visible(timeout=1_000)

        expect(logged_page.locator(
            f"text={self.__class__.ONE_TASK_TEXT}").first
        ).to_be_visible()

    def test_02_add_new_task_for_future(self, do_cleanup):
        logged_page = self.__class__.logged_page

        # Click "Add task" button
        logged_page.locator("span:text('Add task')").first.click()
        logged_page.locator(
            "p[data-placeholder='Description']"
        ).first.wait_for(state="attached", timeout=1_000)

        # Write task text
        logged_page.get_by_role("textbox", name="Task name").fill(self.__class__.TASK_TEXT)

        # Set date
        logged_page.locator('div[aria-label="Set date"]', has_text="Today").click()
        expect(logged_page.locator(
            'div[data-testid="scheduler-view"]').first
        ).to_be_visible(timeout=500)
        logged_page.keyboard.type("10 Aug")
        logged_page.keyboard.press("Enter")

        # Create task
        logged_page.click("button[data-testid='task-editor-submit-button']")

        # Verify task wasn't displayed in "Today" section
        is_task_visible = logged_page.locator(
            'div[class="task_content"]', has_text=self.__class__.TASK_TEXT).first.is_visible()
        assert not is_task_visible

        is_text_visible = logged_page.locator(
            f"text={self.__class__.ONE_TASK_TEXT}").first.is_visible()
        assert not is_text_visible

        # Navigate to "Inbox" section
        logged_page.locator("span:text('Inbox')").first.click(force=True)
        expect(logged_page.locator("h1").nth(1)).to_have_text("Inbox")

        is_task_visible = logged_page.locator(
            'div[class="task_content"]', has_text=self.__class__.TASK_TEXT).first.is_visible()
        assert is_task_visible
