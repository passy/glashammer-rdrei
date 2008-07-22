
import os

# File utilities

def sibpath(path, sibling):
    return os.path.join(os.path.dirname(path), sibling)

