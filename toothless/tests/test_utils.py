from toothless import utils

def test_smartsplit_simple():
    s = utils.smart_split('asdf\nasdfas', maxlen=6, searchcount=5)
    assert s == ['asdf', 'asdfas']

def test_smartsplit_fallback_to_space():
    s = utils.smart_split('123451\n3 512345', 5, 5)
    assert s == ['12345', '1\n3', '51234', '5']

def test_smartsplit_just_split():
    s = utils.smart_split('1234512345', 5, 5)
    assert s == ['12345', '12345']
