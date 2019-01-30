from toothless.commandparser import regex_from_pattern


def test_convert_normal_string():
    regex, argdict = regex_from_pattern('test')
    assert regex.endswith('(?P<__leftover>.*)')
    assert regex.startswith('^test')
