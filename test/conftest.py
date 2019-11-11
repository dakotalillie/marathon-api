from pathlib import Path
from dotenv import load_dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def initialize_environment():
    load_dotenv(dotenv_path=Path("env/test.env"))
