# coding=utf-8

import os
import logging
import re

logger = logging.getLogger('bomb')

def normalize_path(*path):
    '''Normally a path. If the path is a direcotry the last character is 
    path separate.
    '''
    path = os.path.normcase(''.join(path))
    dirname, basename = os.path.split(path)
    # is it a direcotry?
    basename = os.sep if basename == '' else (os.sep if dirname != '' else '')\
        + basename

    return (dirname if dirname == '' else os.path.normpath(dirname))\
        + basename


def filename(path):
    '''Parse a file path return file name, base name and extension name.
    '''

    pattern = re.compile(r'[/\\]([^/\\]+\.\w+$)')
    matchObj = re.search(pattern, path)
    if matchObj:
        filename = matchObj.group(1)
    else:
        filename = path
    pattern = re.compile(r'^(.+)\.(\w+)$')
    matchObj = re.search(pattern, filename)
    if matchObj:
        # (filename, name, extend name)
        return (filename, matchObj.group(1), matchObj.group(2))
    else:
        return (filename)
