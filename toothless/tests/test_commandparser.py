from toothless.commandparser import parse_pathstr
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
