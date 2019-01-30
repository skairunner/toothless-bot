import re


class TokenMismatch(BaseException):
    pass

# The proto tokens and tokens used for the route parsers
class ProtoToken:
    def __init__(self, name):
        self.name = name

    def match(self, string):
        raise TokenMismatch('ProtoToken cannot match anything.')

# A token that is a static string
class StaticProto(ProtoToken):
    def __init__(self, staticstr):
        self.staticstr = staticstr

    def verify(self, string):
        return self.staticstr == string

# A token that represents a string argument
class StringProto(ProtoToken):
    pass

class IntProto(ProtoToken):
    pass

class RealProto(ProtoToken):
    pass

PROTOTOKENS = {
    'str': StringProto,
    'int': IntProto,
    'real': RealProto
}

class Token:
    pass
