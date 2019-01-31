import pytest
from toothless import commandrouter as cr
from toothless import tokens as tok

def test_match_prototokens_to_tokens_success():
    # Case 1: Ending with a Remainder proto
    prototokens = [tok.RemainderProto('nom')]
    tokens = ['first', 'second', 'third']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (1, 3)
    assert len(results) == 1
    assert results[0] == 'first second third'
    # Case 2: Equal tokens to paths
    prototokens = [tok.IntProto('int'), tok.StringProto('str')]
    tokens = ['143', 'a s d f']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (2, 2)
    assert results[0] == 143
    assert results[1] == 'a s d f'
    # Case 3: More tokens than paths
    tokens = ['1', 'a', 'b']
    results, matchcount = cr.match_prototokens_to_tokens(prototokens, tokens)
    assert matchcount == (2, 2)
    assert results[1] == 'a'

def test_match_prototokens_toomanyproto():
    prototokens = [tok.IntProto('int'), tok.IntProto('int')]
    tokens = ['1']
    with pytest.raises(cr.PathMismatch):
        cr.match_prototokens_to_tokens(prototokens, tokens)

# Not all tokens before the Remainder token match
def test_match_prototokens_remainder_not_enough():
    prototokens = [tok.IntProto('int'), tok.RemainderProto('r')]
    tokens = ['asd']
    with pytest.raises(cr.PathMismatch):
        cr.match_prototokens_to_tokens(prototokens, tokens)
