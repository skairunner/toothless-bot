import re
from enum import Enum


# Raised if a ProtoToken is given an input string that does not match the 
# token type it represents.
class TokenMismatch(BaseException):
    pass

# The proto tokens and tokens used for the route parsers
class ProtoToken:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<{self.__class__.__name__}:{self.name}>'

    def match(self, string):
        raise TokenMismatch('ProtoToken cannot match anything.')

# A token that is a static string
class StaticProto(ProtoToken):
    def __init__(self, staticstr):
        self.name = 'STATIC'
        self.staticstr = staticstr

    def verify(self, string):
        if self.staticstr != string:
            raise TokenMismatch()
        return string

# A token that represents a string argument
class StringProto(ProtoToken):
    def verify(self, string):
        return string

class IntProto(ProtoToken):
    def verify(self, string):
        try:
            return int(string)
        except ValueError:
            raise TokenMismatch(f'The string "{string}" is not a valid integer.')

class RealProto(ProtoToken):
    def verify(self, string):
        try:
            return float(string)
        except ValueError:
            raise TokenMismatch(f'The string "{string}" is not a valid float.')

BOOL_TRUTHY = set(['true', 'yes', 'y', '1'])
BOOL_FALSEY = set(['false', 'no', 'n', '0'])
class BoolProto(ProtoToken):
    def verify(self, string):
        if string in BOOL_TRUTHY:
            return True
        if string in BOOL_FALSEY:
            return False
        raise TokenMismatch(f'The string "{string}" is not a valid boolean-y value.')

# This special token 'slurps' all tokens after it.
class RemainderProto(ProtoToken):
    def verify(self, string):
        return string


class TokenizerState(Enum):
    NORMAL = 1
    QUOTED_SINGLE = 2
    QUOTED_DOUBLE = 3
    QUOTED_BACK = 4
    MUST_SPACE = 5  # After a quote, MUST be a space (or EOL)


STATE_FROM_QUOTE = {
    '`': TokenizerState.QUOTED_BACK,
    "'": TokenizerState.QUOTED_SINGLE,
    '"': TokenizerState.QUOTED_DOUBLE
}


PROTOTOKENS = {
    'str': StringProto,
    'int': IntProto,
    'real': RealProto,
    'bool': BoolProto,
    '*': RemainderProto
}
