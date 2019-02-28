'''
Provided a discord.py user, returns <username>#<discriminator>,
e.g. Discorder#1029.
'''
def get_full_username(user):
    return f'{user.name}#{user.discriminator:0>4}'

# Splits input into 2000ch or less blocks, attempting to preserve
# formatting and prefering to split on \n and space over mid-word
# :returns: array of strings
def smart_split(string, maxlen=2000, searchcount=50):
    out = []
    while len(string) > maxlen:
        # Find nearest \n
        found = False
        for i in range(maxlen - 1, maxlen - searchcount + 1, -1):
            if string[i] == '\n':
                out.append(string[:i])
                string = string[i+1:]
                found = True
                break
        if not found:
            # find nearest space instead
            for i in range(maxlen - 1, maxlen - searchcount + 1, -1):
                if string[i] == ' ':
                    out.append(string[:i])
                    string = string[i+1:]
                    found = True
                    break
        if not found:
            # just hard break
            out.append(string[:maxlen])
            string = string[maxlen:]
    out.append(string)
    return out
