# coding=utf-8

import re
import json
import logging

logger = logging.getLogger('bomb')

class Config(object):
	def __init__(self):
		pass

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
		try:
			self._config.update(config)
		except AttributeError:
			self._config = config

		logger.debug('Load config file : ' + path)

	def get(self, key):
		try:
			return self._config[key]
		except KeyError:
			return None

	def set(self, key, value):
		try:
			self._config[key] = value
		except AttributeError:
			self._config = {}
			self._config[key] = value