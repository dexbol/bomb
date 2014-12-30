# coding=utf-8

import re
import json
import logging

logger = logging.getLogger('bomb')

try:
    WindowsError
except NameError:
    WindowsError = None

class Config(dict):

    def load(self, path):
        try:
            result = []
            rcomment = re.compile(r'^\s*\/\/')
            with open(path) as handler:
                for line in handler:
                    if not re.search(rcomment, line):
                        result.append(line)
        except (IOError, WindowsError):
            logger.warning('config file is not exsit:' + path)

        config = json.loads(''.join(result))
        self.update(config)
        logger.debug('Load config file : ' + path)

    def get(self, key):
        return self[key]

    def set(self, key, value):
        self[key] = value    





