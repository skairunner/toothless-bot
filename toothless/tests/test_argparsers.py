import pytest
import toothless.argparsers as A

iparse = A.IntParser()
rparse = A.RealParser()
sparse = A.StrParser()

# can't use the base class
def test_cant_use_argparser():
    with pytest.raises(A.ArgParserError):
        argparse = A.ArgParser()
        argparse.parse('asdf')

def test_int_parser():
    assert iparse.parse('1234') == (1234, 4)

def test_int_parser_leftovers():
    assert iparse.parse('1234 1234') == (1234, 4)
    assert iparse.parse('1234s') == (1234, 4)

def test_int_parser_negatives():
    assert iparse.parse('-14') == (-14, 3)

def test_int_parser_no_floats():
    assert iparse.parse('1.23') == (1, 1)
    with pytest.raises(A.ParseArgumentMismatch):
        iparse.parse('-.5')
    with pytest.raises(A.ParseArgumentMismatch):
        iparse.parse('asdf')

def test_int_parser_only_matches_start_of_string():
    with pytest.raises(A.ParseArgumentMismatch):
        iparse.parse('as 123')

def test_parse_floats():
    assert rparse.parse('1.2') == (1.2, 3)
    assert rparse.parse('.2') == (.2, 2)
    assert rparse.parse('-6.32') == (-6.32, 5)

def test_parse_string():
    s = 'asjc dmc weoi'
    slen = len(s)
    assert sparse.parse(s) == (s, slen)
