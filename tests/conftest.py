import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--runintegration",
        action="store_true",
        default=False,
        help="run integration tests"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark integration tests")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--runintegration"):
        return
    skip_integration = pytest.mark.skip(reason="need --runintegration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)

