# coding=utf-8

import logging
import os
import shutil
import time
from .cfilegroup import CFileGroup
from .config import Config
from .utils import normalize_path
from .svn import *
from .compiler import compile_csjs

logger = logging.getLogger('bomb')

class Batch():

	def __init__(self, config_path=None, **kwargs):

		default_params = {
			"cfile": [],
			"referrer": [],
			"store": '',
			"prefix_path": None,
			"debug": False
		}

		base_url = ''
		params = dict()

		if config_path:
			config = Config()
			config.load(config_path)
			base_url = (os.path.dirname(config_path) or '.') + os.sep
			params = config
		else:
			params = kwargs

		for key, value in default_params.iteritems():
			params.setdefault(key, value)

		if not len(params['cfile']):
			raise Exception('Config Error: cfile requires.')
		if not params['store']:
			raise Exception('Config Error: store requires')


		referrer = params['referrer']
		store = params['store']
		tempath = normalize_path(base_url + 'bomb-' + str(int(time.time())) + '/')

		group = CFileGroup()
		for path in params['cfile']:
			group.add_by_path(normalize_path(base_url + path), 
				url_base=base_url, url_map=params['prefix_path'])

		self.group = group
		self.debug = params['debug']
		self.base_url = base_url
		self.referrer = [self._path(refer) for refer in referrer]
		self.store = self._path(store)
		self.tempath = tempath

	def _verify_param(self, param):
		pass

	def _path(self, path):
		return normalize_path(self.base_url + path)

	def _svn_update(self, path):
		path = path if isinstance(path, list) else [path]
		for p in path:
			logger.info('svn update: ' + p)
			svn_update([p])

	def _svn_commit(self, path):
		path = path if isinstance(path, list) else [path]
		for p in path:
			logger.info('svn commit: ' + p)
			svn_commit([p])

	def _svn_lock(self, path):
		path = path if isinstance(path, list) else [path]
		for p in path:
			logger.info('svn lock: ' + p)
			svn_lock([p])

	def _svn_unlock(self, path):
		path = path if isinstance(path, list) else [path]
		for p in path:
			logger.info('svn unlock: ' + p)
			svn_unlock([p])		

	def _svn_remove(self, path):
		path = path if isinstance(path, list) else [path]
		for p in path:
			logger.info('svn remove: ' + p)
			svn_remove([p])

	def list(self):
		return ['[' + str(item.index) + ']' + item.filename +
			('(bootstrap)' if item.bootstrap else '') +
			('(placeholder)' if item.placeholder else '') 
			for item in self.group.list(True)]

	def filter(self, select=[]):
		self.group.filter(select)
		logger.info('The following cfile will be compiled:')
		for item in self.group.list():
			logger.info('[' + str(item.index) + ']' + item.filename +\
				('(bootstrap)' if item.bootstrap else ''))

	def update_workspace(self):
		self._svn_update(self.referrer)
		self._svn_update(self.store)
		self._svn_update(self.base_url)

	def lock_workspace(self):
		self._svn_lock(self.referrer)
		self._svn_lock([item.path for item in self.group.list()])

	def unlock_workspace(self):
		self._svn_unlock(self.referrer)
		self._svn_unlock([item.path for item in self.group.list()])


	def commit(self):
		preflighter = [self.store + item.get_version_name()\
			for item in self.group.list()]

		self._svn_commit(preflighter)
		self._svn_commit(self.referrer)
		self._svn_commit([item.path for item in self.group.list()])

	def remove_stale(self):
		try:
			WindowsError
		except NameError:
			WindowsError = None

		recycel = []
		try:
			for item in self.group.list():
				path = self.store + item.get_stale_name()
				os.remove(path)
				recycel.append(path)
		except IOError:
			pass
		except WindowsError:
			pass
		except OSError:
			pass
		finally:
			self._svn_remove(recycel)

	def publish(self):
		self.update_workspace()
		self.lock_workspace()

		group = self.group
		tempath = self.tempath
		store = self.store
		referrer = self.referrer

		try:
			os.mkdir(tempath)
			group.update_version()

			for path in group.push_list(tempath):
				filename = os.path.basename(path)
				logger.info('compile: ' + store + filename)
				compile_csjs(path, store + filename)

			for refer in referrer:
				group.update_referrer(refer)

			self.unlock_workspace()
			self.commit()
			self.remove_stale()

			if not self.debug:
				shutil.rmtree(tempath)

		finally:
			self.unlock_workspace()







