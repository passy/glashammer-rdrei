# -*- coding: utf-8 -*-
"""
    glashammer.utils.fileutils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Ali Afshar
    :license: MIT
"""
import os

# File utilities

def sibpath(path, sibling):
    return os.path.join(os.path.dirname(path), sibling)

