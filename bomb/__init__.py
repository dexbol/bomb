# coding=utf-8

import logging
import os
import sys
import argparse
import re
from cmd import Cmd

from . import mapscan
from .utils import normalize_path, filename
from .cfile import CFile
from .cfilegroup import CFileGroup
from .compiler import *
from .config import Config
from .svn import *
from .batch import Batch
from .init import init_config

class LoggerFormatter(logging.Formatter):

    def format(self, record):
        if record.levelno <= logging.INFO:
            self._fmt = '%(msg)s'

        return logging.Formatter.format(self, record)


logger = logging.getLogger('bomb')
logger_handler = logging.StreamHandler()
logger_handler.setLevel(logging.DEBUG)
logger_formatter = LoggerFormatter('%(filename)s> %(message)s')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)


class Publish(Cmd):

    _intro = '''
*************************************************************
*                                                           *
*  Six Rooms Front-end Publish Tools.                       *
*  Type "help" for command information.                     *
*                                                           *
*************************************************************'''

    prompt = '>> '

    def __init__(self, config_path):
        Cmd.__init__(self)

        self._print(self._intro)

        if config_path:
            self.batch = Batch(config_path)
            self.do_list(None)

    def do_list(self, arg):
        ''' list cfile group if it exists'''
        try:
            batch = self.batch
            self._print('---')
            self._print(batch.list())
            self._print(['---', 
                'Type cfile\'s index segemeny by comma to parse,e.g. 2,12,4',
                'Type \'all\' to parse all cfile'])

        except AttributeError:
            self._print('*** You Can\'t Use This Command.')

    def do_exit(self, *args):
        ''' exit bomb console '''
        return True

    def do_scanmap(self, path):
        '''Scan all cfile in the dirctory
        '''
        path = path or os.getcwd()
        mapscan.write(path)
        self._print('Scan Complete!!')
        return True

    def do_publish(self, selected):
        '''Publish selected cfiles. e.g. publish 2,12,4 .
        you can specify a version name like this: 2-12,3-3. That's means the cfile index
        is 2, it's version could be 12 '''

        if selected:
            try:
                batch = self.batch

                if selected != 'all':
                    explode = selected.strip().split(',')
                    selected = [idx.strip() for idx in explode]
                    index = []
                    specifyVersion = []

                    for sel in selected:
                        explode = sel.split('-')
                        index.append(int(explode[0]))
                        try:
                            version = explode[1]
                            specifyVersion.append((
                                int(explode[0]),
                                # batch.publish will update all cfiles be 
                                # publish (version += 1) so minus 1 here
                                int(version) - 1
                                ))
                        except IndexError:
                            pass

                    batch.filter(index)

                    group = batch.group
                    for index, version in specifyVersion:
                        try:
                            group.index(index).version = version
                            
                        except AttributeError:
                            pass

                batch.publish()
                self._print('Publish Complete!! Press Enter To Exit.')

            except AttributeError as e:
                self._print(e)
                self._print('*** You Can\'t Use This Command.')
        else:
            self._print('*** Arguments Error')

    def do_init(self, path):
        '''Initialize cfile directory: create config.json in the directory
    if it not exsit. You shoud edit config.json as your need. 
        '''
        path = path or os.getcwd()
        result = init_config(path)
        if result:
            self._print('Create ' + result)

    def do_help(self, arg):
        if arg:
            try:
                doc = getattr(self, 'do_' + arg).__doc__
                if doc:
                    self._print(str(doc))
                    return
            except AttributeError:
                pass
        else:
            names = self.get_names()
            docs = {}
            for name in names:
                if name[0:3] != 'do_':
                    continue
                try:
                    doc = getattr(self, name).__doc__
                    if doc:
                        docs[name[3:]] = doc
                except AttributeError:
                    pass

            self._print('-------------')
            self._print('Commands List')
            self._print('-------------')
            for command, doc in docs.items():
                self._print(command + ' - ' + doc)

    def emptyline(self):
        return True

    def precmd(self, line):
        if line:
            pattern = re.compile(r'''^\s*all\s*$|
                ^(\s*\d+(-\d+)?\s*,?\s*)+$''', re.VERBOSE)
            if re.search(pattern, line):
                return 'publish ' + line.strip()
        return line        

    def _print(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self._print(m)
        else:
            self.stdout.write('%s\n' % msg)


def run(config_path=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', nargs='?')
    args = parser.parse_args()
    logger.setLevel(logging.INFO)

    publisher = Publish(config_path or args.config_path)
    publisher.cmdloop()




