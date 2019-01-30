import re
from .argparsers import ARG_PARSERS
from . import tokens as tok

# used for finding <:> format args
ARG_PATTERN = re.compile(r'<(?P<name>[A-Za-z_][\w]*):(?P<type>int|str|real)>')
# convert <:> format args into the actual regex to match
ARG_REGEX_TEMPLATE = '(?P<{name}>{pattern})'


class ArgumentNameDuplicateError(IndexError):
    pass


"""
Parses <:> command syntax into regexes.

:param pattern: The pattern to convert into a regex
:returns: Tuple of (compiled regex pattern, parser dict by name)
"""
def regex_from_pattern(patternstring):
    groups = list(ARG_PATTERN.finditer(patternstring))
    frags = []
    # Append the first bit
    end = None if len(groups) == 0 else groups[0].start()
    frags.append(patternstring[:end])
    for i, group in enumerate(groups):
        frags.append(group)
        start = group.end()
        end = groups[i+1].start() if i < len(groups) - 1 else None
        frags.append(patternstring[start:end])
    # frags is now an array of strings and Match objects.
    # Escape strings, and convert Match objects into regexes
    regex_bits = ['^']  # only match to the beginning
    parsers = {}
    for frag in frags:
        if isinstance(frag, str):
            regex_bits.append(re.escape(frag))
        else:
            name = frag['name']
            parser = ARG_PARSERS[frag['type']]
            if name in parsers:
                raise ArgumentNameDuplicateError(
                    f'There is more than one of name "{name}" in the route "{patternstring}"')
            parsers[name] = parser
            regex_bits.append(ARG_REGEX_TEMPLATE.format(
                name=name, pattern=parser.pattern.patternstring)
            )
    return (r'\s+'.join(regex_bits), parsers)


"""
Parses <:> format pathstr. All extra whitespace is removed.
:param pathstr: The pathstr to parse
:returns: Array of prototokens to match inputs against
"""
def parse_pathstr(pathstr):
    sections = re.split(r'\s+', pathstr)
    prototokens = []
    # Convert args into ProtoTokens
    for string in sections:
        maybematch = ARG_PATTERN.match(string)
        if maybematch is not None:
            name = maybematch.group('name')
            type_ = maybematch.group('type')
            prototoken = tok.PROTOTOKENS[type_]
            prototokens.append(prototoken(name))
        else:
            prototokens.append(tok.StaticProto(string))
    return prototokens
