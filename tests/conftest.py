import pytest

def pytest_addoption(parser):
    parser.addini("test_url", "URL for testing", type="string")
    parser.addini("api_url", "API URL for testing", type="string")
    parser.addini("test_username", "Username for testing", type="string")
    parser.addini("test_password", "Password for testing", type="string")

@pytest.fixture(scope='class')
def get_config(request):
    return {
        "test_url": request.config.getini("test_url"),
        "api_url": request.config.getini("api_url"),
        "test_username": request.config.getini("test_username"),
        "test_password": request.config.getini("test_password")
    }
