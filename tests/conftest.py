import os
import pathlib

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
pathlib.Path("test.db").unlink(missing_ok=True)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
    pathlib.Path("test.db").unlink(missing_ok=True)
