# demo-pytest-playwright
Demo project that uses pytest-playwright for testing

## How to use?
1. Clone the repository by executing "git clone"
2. Navigate to cloned directory
3. Execute "python3 -m venv .venv" to create virtual environment (on Windows use "python -m venv .venv")
4. Activate venv by executing "source .venv/bin/activate" (on Windows use ".venv\Scripts\activate")
5. Execute "pip install -r requirements.txt" to install requirements
6. Change "test_username" and "test_password" params in pytest.ini to actual registered login email and password (https://app.todoist.com)
7. Run tests by executing "pytest"

The last command runs two tests from TestAddNewTask class.
