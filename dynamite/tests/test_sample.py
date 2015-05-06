__author__ = 'brnr'

import pytest

def func(x):
    return x + 1

def raisingError():
    raise SystemExit(1)

def test_answer():
    assert func(3) == 4

# Test raising of exceptions
def test_an_exception():
    with pytest.raises(IndexError):
        [5,10,15][30]

def test_raisingError():
    with pytest.raises(SystemExit):
        raisingError()


# Defining TestClass
# Works automagically because starting with "Test"
class TestClass(object):
    def test_one(self):
        x = "this"
        assert 'h' in x


# Functional / Fixtures
# The magic word here is 'tmpdir'
def test_needsfiles(tmpdir):
    print(tmpdir)
    assert 1