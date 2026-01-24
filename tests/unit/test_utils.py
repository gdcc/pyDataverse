from pyDataverse import utils

def test_clean_string():
    assert utils.clean_string("  Hello  World!  ") == "Hello World!"