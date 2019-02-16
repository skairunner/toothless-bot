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

# Specify names of modules to import on load to activate event handlers
event_handler_modules = []

# If True, will never crash on exception in a route handler.
# Warning: This may cause corruption of data or invalid state, depending on
# the plugin in question
GRACEFULLY_CATCH_EXCEPTIONS = False

from config import *
