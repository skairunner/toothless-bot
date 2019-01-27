from toothless import commandrouter as cr
from hello import hello_world


prefix_patterns = [
    cr.path('hi', hello_world)
]
