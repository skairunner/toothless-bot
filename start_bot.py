import toothless
from config import prefix_patterns, TOKEN, COMMAND_PREFIX


if __name__ == '__main__':
    toothless.run_bot(TOKEN, prefix_patterns, COMMAND_PREFIX)
