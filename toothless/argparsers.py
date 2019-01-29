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
        if not isinstance(self.pattern, re.Pattern):
            raise ArgParserError(f'The pattern for {self.__class__} has not been specified.')

        match = self.pattern.match(string)
        if match is None or match == 0:
            raise ParseArgumentMismatch(
                f'{self.__class__}: Attempted to match "{self.pattern.pattern}" against "{string}", failed.'
            )
        return (self.convert_match(match), match.end())

    # Convert a matched string into the appropriate Python object
    def convert_match(self, match):
        return match


class IntParser(ArgParser):
    pattern = re.compile('-?\d+')

    def convert_match(self, match):
        return int(match)


class StrParser(ArgParser):
    pattern = re.compile(r'.+')

    def convert_match(self, match):
        return match


class RealParser(ArgParser):
    pattern = re.compile(r'-?\d*\.?\d+')

    def convert_match(self, match):
        return float(match)


ARG_PARSERS = {
    'str': StrParser(),
    'int': IntParser(),
    'real': RealParser()
}
