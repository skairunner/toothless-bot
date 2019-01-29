import re
from argparsers import ARG_PARSERS


ARG_PATTERN = re.compile(r'<(?P<name>[A-Za-z_][\w]*):(?P<type>int|str|real)>')

"""
Parses <:> command syntax into regexes.

:param pattern: The pattern to convert into a regex
:returns: Regex pattern to match paths
"""
def regex_from_pattern(patternstring):
    groups = ARG_PATTERN.findall(patternstring)
    frags = []
    for i, group in enumerate(groups):
        start = groups[i-1].end() if 0 < i else None
        end = groups[i+1].start() if i < len(groups)-1 else None
        frags.append(patternstring[start:end])
        frags.append
