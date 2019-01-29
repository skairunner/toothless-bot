import re


class ParseArgumentMismatch(BaseException):
    pass


class ArgParserError(BaseException):
    pass


class ArgParser:
    pattern = None

    """
    Attempts to match off the string, starting from the beginning.

    :param string: The string to match against
    :returns: Tuple (matchresult, endindex)
    :raises: ParseArgumentMismatch if the match fails or is empty
    """
    def parse(self, string):
        if self.pattern is None:
            raise ArgParserError(f'{self.__class__}: Pattern must be set.')
        match = re.match(self.pattern, string)
        if match is None or match == 0:
            raise ParseArgumentMismatch(
                f'{self.__class__}: Attempted to match "{self.pattern.pattern}" against "{string}", failed.'
            )
        return (self.convert_match(match), match.end())

    # Convert a matched string into the appropriate Python object
    def convert_match(self, match):
        return match


class IntParser(ArgParser):
    pattern = re.compile(r'-?\d+')

    def convert_match(self, match):
        return int(match.group(0))


class StrParser(ArgParser):
    pattern = re.compile(r'.+')

    def convert_match(self, match):
        return match.group(0)


class RealParser(ArgParser):
    pattern = re.compile(r'-?\d*\.?\d+')

    def convert_match(self, match):
        return float(match.group(0))


ARG_PARSERS = {
    'str': StrParser(),
    'int': IntParser(),
    'real': RealParser()
}
