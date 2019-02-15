"""
Set defaults for config options
"""
import os

# The token to authenticate to Discord with
TOKEN = os.environ['BOTTOKEN']

# All prefix commands must start with this sigil
# It must be 0 or 1 characters
COMMAND_PREFIX = '/'

# Must specify routes in config
prefix_patterns = []

from config import *
