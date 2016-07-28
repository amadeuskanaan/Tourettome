__author__ = 'kanaan'

import string
valid_chars = '-_.() %s%s' %(string.ascii_letters, string.digits)

def mkdir_path(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def mkcd_path(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    os.system(path)

def find(name, path):
    import os
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)