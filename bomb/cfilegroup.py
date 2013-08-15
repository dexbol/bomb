# coding=utf-8

import os
from bomb.cfile import CFile
from bomb.utils import normalize_path, filename


class CFileGroup(object):

	def __init__(self):
		self._list = []

	def add(self, cfile):
		cfile.index = len(self._list)
		self._list.append(cfile)

	def add_by_path(self, path, url_base=None, url_map=dict()):
		# directory
		if path.endswith(os.sep):
			for dirpath, dirname, filenames in os.walk(path):
				# only walk top fold level
				if dirpath != path:
					continue
				for f in filenames:
					if f.endswith('.js') or f.endswith('.css'):
						path = normalize_path(dirpath + os.sep + f)
						self.add(CFile(path, url_base=url_base, url_map=url_map))

		else:
			self.add(CFile(path, url_base=url_base, url_map=url_map))


	def filter(self, selected=[]):
		has_js = False

		for item in self._list:
			if item.index in selected:
				item.frozen = False
				if item.extension == 'js':
					has_js = True
			else:
				item.frozen = True

		if has_js:
			for item in self._list:
				if item.bootstrap:
					item.frozen = False

	def pick(self, name):
		for item in self._list:
			if item.filename == name:
				return item
		return None

	def list(self, whole=False):
		for item in self._list:
			if not item.frozen or whole:
				yield item

	def dump(self, name):
		cfile = self.pick(name)
		extension = [] if not cfile.bootstrap else self.collect_map() 			
		return cfile.dump(extension)

	def push(self, name, destination):
		cfile = self.pick(name)
		extension = [] if not cfile.bootstrap else self.collect_map()
		return cfile.push(destination, extension)

	def push_list(self, destination):
		path = []

		for item in self.list():
			if not item.bootstrap:
				path.append(self.push(item.filename, destination))

		for item in self.list():
			if item.bootstrap:
				path.append(self.push(item.filename, destination))

		return path

	def update_version(self):
		for item in self.list():
			item.update_version()

	def update_referrer(self, referrer, pattern=None, repl=None):
		for item in self.list():
			item.update_referrer(referrer, pattern=pattern, repl=repl)

	def collect_map(self):
		return [item.map for item in self.list(True)]

	def collect_stale(self, direct):
		return [normalize_path(direct + item.get_stale_name()) for
			item in self.list()]






