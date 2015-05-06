__author__ = 'brnr'

import pytest

@pytest.fixture(scope="module")
def scope_data():
    return {"count": 0}


def test_first(scope_data):
    assert scope_data["count"] == 0
    scope_data["count"] += 1


def test_second(scope_data):
    assert scope_data["count"] == 1