__author__ = 'brnr'

import pytest

@pytest.fixture # Registering this function as a fixture
def complex_data():
    # Creating test data entirely in this function to isolate
    #  it from the rest of this module
    class DataTypes(object):
        string = str
        list = list
    return DataTypes()

def test_types(complex_data):
    assert isinstance("Elephant", complex_data.string)
    assert isinstance([1,2,3], complex_data.list)

def test_complex_data(complex_data):
    assert isinstance(complex_data, object)
    assert complex_data.string == str
    assert complex_data.list == list