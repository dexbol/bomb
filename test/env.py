# coding=utf-8

import sys
import os

sys.path.insert(0, os.path.dirname(__file__) + os.sep + '..')

from bomb import normalize_path

test_path = normalize_path(os.path.dirname(__file__) + os.sep)
root_path = normalize_path(test_path + '../')

