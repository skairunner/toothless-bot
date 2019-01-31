import pytest
from toothless.commandparser import parse_pathstr, tokenize, ParserError
from toothless import tokens as t


def test_convert_simple_path():
    arr = parse_pathstr('test')
    assert len(arr) == 1
    assert arr[0].staticstr == 'test'

def test_convert_int_path():
    arr = parse_pathstr('a <b:int>')
    assert arr[0].staticstr == 'a'
    assert arr[1].name == 'b'
    assert isinstance(arr[1], t.IntProto)

def test_convert_sandwiched_path():
    arr = parse_pathstr('command that <is:str> sandwiched')
    assert len(arr) == 4
    assert isinstance(arr[2], t.StringProto)
    assert arr[2].name == 'is'

def test_ignore_nospace_argument():
    arr = parse_pathstr('state<is:str>')
    assert len(arr) == 1

def test_tokenize_simple_string():
    arr = tokenize('state')
    assert arr[0] == 'state'

def test_tokenize_multiple_strings():
    arr = tokenize('state the way 123')
    assert arr[0] == 'state'
    assert arr[3] == '123'

def test_tokenize_quotes():
    arr = tokenize('this "is three" tokens')
    assert len(arr) == 3
    assert arr[1] == 'is three'
    arr = tokenize("this 'is also three' tokens")
    assert len(arr) == 3
    assert arr[1] == 'is also three'
    arr = tokenize('this `is, as well, three` tokens')
    assert len(arr) == 3
    assert arr[1] == 'is, as well, three'

def test_tokenize_errors_if_no_space_after_quote():
    with pytest.raises(ParserError):
        tokenize('this "quote"has no space after it')
