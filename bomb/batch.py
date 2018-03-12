# coding=utf-8

import logging
import os
import shutil
import time
import ftplib
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
            "scss_root": None,
            "debug": False,
            "ftp_ip": "",
            "ftp_port": "",
            "ftp_username": "",
            "ftp_password": "",
            "ftp_root": ""
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

        for key, value in default_params.items():
            params.setdefault(key, value)

        if not len(params['cfile']):
            raise Exception('Config Error: cfile requires.')

        referrer = params['referrer']
        store = params['store']
        tempath = normalize_path(base_url + 'bomb-' + \
                    str(int(time.time())) + '/')
        tempstorepath = normalize_path(base_url + 'bomb-stor-' + \
                    str(int(time.time())) + '/')
        scss_root = normalize_path(base_url + params['scss_root']) if \
                    params['scss_root'] else None

        group = CFileGroup()
        for path in params['cfile']:
            group.add_by_path(normalize_path(base_url + path), 
                url_base=base_url, 
                url_map=params['prefix_path'], 
                scss_root=scss_root)

        self.group = group
        self.debug = params['debug']
        self.base_url = base_url
        self.referrer = [self._path(refer) for refer in referrer]
        self.store = self._path(store) if store else tempstorepath
        self.tempath = tempath
        self.tempstorepath = tempstorepath
        self.config = params

    def _verify_param(self, param):
        pass

    def _path(self, path):
        return normalize_path(self.base_url + path)

    def _svn_update(self, path):
        path = path if isinstance(path, list) else [path]
        if self._svn_check(path):
            for p in path:
                logger.info('svn update: ' + p)
                svn_update([p])
        else:
            logger.info('!ignore svn update: ' + ' '.join(path))

    def _svn_commit(self, path):
        path = path if isinstance(path, list) else [path]
        if self._svn_check(path):
            for p in path:
                logger.info('svn commit: ' + p)
                svn_commit([p])
        else:
            logger.info('!ignore svn commit: ' + ' '.join(path))

    def _svn_lock(self, path):
        path = path if isinstance(path, list) else [path]
        if self._svn_check(path):
            for p in path:
                logger.info('svn lock: ' + p)
                svn_lock([p])
        else:
            logger.info('!ignore svn lock: ' + ' '.join(path))

    def _svn_unlock(self, path):
        path = path if isinstance(path, list) else [path]
        if self._svn_check(path):
            for p in path:
                logger.info('svn unlock: ' + p)
                svn_unlock([p])
        else:
            logger.info('!ignore svn unlock: ' + ' '.join(path))

    def _svn_remove(self, path):
        path = path if isinstance(path, list) else [path]
        if self._svn_check(path):
            for p in path:
                logger.info('svn remove: ' + p)
                svn_remove([p])
        else:
            logger.info('!ignore svn remove: ' + ' '.join(path))

    def _svn_check(self, path):
        try:
            svn_command('info', [os.path.dirname(path[0])])
            return True
        except (SVNError, IndexError):
            return False

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

    def ftp(self):
        files = [self.store + item.get_version_name()\
            for item in self.group.list()]
        config = self.config;
        client = ftplib.FTP()
        client.connect(config['ftp_ip'].encode('utf-8'), 
                        config['ftp_port'].encode('utf-8'))
        client.login(config['ftp_username'].encode('utf-8'), 
                        config['ftp_password'].encode('utf-8'))
        client.cwd(config['ftp_root'].encode('utf-8'))
        for item in self.group.list():
            with open(self.store + item.get_version_name()) as handler:
                client.storbinary('STOR ' + item.get_version_name(), handler)

    def publish(self):
        useftp = bool(self.config['ftp_ip'])

        if not useftp:
            self.update_workspace()
            self.lock_workspace()

        group = self.group
        tempath = self.tempath
        tempstorepath = self.tempstorepath
        store = self.store
        referrer = self.referrer

        try:
            os.mkdir(tempath)
            os.mkdir(tempstorepath)
            group.update_version()

            for path in group.push_list(tempath):
                filename = os.path.basename(path)
                logger.info('compile: ' + store + filename)
                compile_csjs(path, store + filename)

            for refer in referrer:
                group.update_referrer(refer)

            if not useftp:
                self.unlock_workspace()
                self.commit()
                self.remove_stale()
            else:
                self.ftp()

            if not self.debug:
                shutil.rmtree(tempath)
                shutil.rmtree(tempstorepath)

        finally:
            if not useftp:
                self.unlock_workspace()
