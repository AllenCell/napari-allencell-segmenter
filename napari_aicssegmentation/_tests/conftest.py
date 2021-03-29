import pytest

@pytest.fixture(autouse=True)
def setup_qt(qapp):
    # the pytestqt.qapp fixture sets up the QApplication required to run QT code
    # see https://pytest-qt.readthedocs.io/en/latest/reference.html
    yield
