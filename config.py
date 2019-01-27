from toothless import commandrouter as cr
from hello import hello_world
import logging
import os


logging.basicConfig(level=logging.INFO)

TOKEN = os.environ['BOTTOKEN']

prefix_patterns = [
    cr.path('hi', hello_world)
]
