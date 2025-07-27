import re
import time
import json
import requests

import pytest
from playwright.sync_api import Browser
from tests.login import Login


class TestAddNewTask:
    logged_page = None
    user_token = None

    @pytest.fixture(scope="class", autouse=True)
    def setup_logged_page(self, get_config, browser: Browser):
        context = browser.new_context()
        page = context.new_page()

        login = Login(page)
        logged_page = login.perform_login(get_config)

        self.__class__.logged_page = logged_page

        yield logged_page
        logged_page.close()

    @pytest.fixture(scope="class")
    def do_cleanup(self, get_config):
        yield
        logged_page = self.__class__.logged_page
        logged_page.wait_for_timeout(2000) # wait for backend response to create tasks

        user_str = logged_page.evaluate("() => localStorage.getItem('User')")
        user_dict = json.loads(user_str)
        user_token = user_dict.get('token', None)

        api_url = get_config['api_url']
        headers = {"Authorization": f"Bearer {user_token}"}

        list_items = logged_page.locator("div[data-viewport-type='window'] div[data-testid='virtuoso-item-list'] li")
        list_items_count = list_items.count()

        # Get all create task ids
        data_item_ids = []
        for i in range(list_items_count):
            li = list_items.nth(i)
            task_id = li.get_attribute("data-item-id")
            if task_id:
                data_item_ids.append(task_id)

        # Send DELETE requests for each task
        for task_id in data_item_ids:
            delete_task_url = f"{api_url}/tasks/{task_id}"

            response = requests.delete(delete_task_url, headers=headers)
            assert 200 <= response.status_code < 300

    def test_add_new_task(self):
        logged_page = self.__class__.logged_page

        logged_page.locator(
            "div", has_text=re.compile("add task", re.IGNORECASE)
        )

        logged_page.click("button[class='plus_add_button']")
        logged_page.locator(
            "p[data-placeholder='Description']"
        ).first.wait_for(state="attached", timeout=1_000)

        logged_page.get_by_role("textbox", name="Task name").fill(TestAddNewTask.TASK_TEXT)
        logged_page.click("button[data-testid='task-editor-submit-button']")


    # def test_add_new_task2(self):
    #     logged_page = self.__class__.logged_page
    #
    #     # logged_page.locator(
    #     #     "div", has_text=re.compile("add task", re.IGNORECASE)
    #     # )
    #
    #     logged_page.click("//button[.//span[text()='Cancel']]")
    #     # logged_page.locator(
    #     #     "p[data-placeholder='Description']"
    #     # ).first.wait_for(state="attached", timeout=1_000)
    #     #
    #     # logged_page.get_by_role("textbox", name="Task name").fill(TestAddNewTask.TASK_TEXT)
    #
    #     time.sleep(10)

        