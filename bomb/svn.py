# coding=utf-8

import subprocess
import logging

logger = logging.getLogger('bomb')

__all__ = ['svn_command', 'svn_update', 'svn_commit', 'svn_remove',
    'svn_lock', 'svn_unlock', 'SVNError']


class SVNError(Exception):
    def __init__(self, command, msg):
        self.command = command
        self.msg = msg

    def __str__(self):
        return str(self.msg)


def svn_command(command, args):
    lines = ['svn', command]
    lines += args

    proc = subprocess.Popen(lines, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()
    if proc.returncode != 0:
        raise SVNError(command, stderrdata)

    return stdoutdata


def verbose_svn_command(command, args):
    try:
        svn_command(command, args)
    except SVNError as e:
        logger.warn(e)


def svn_update(path):
    verbose_svn_command('update', path)


def svn_commit(path):
    try:
        for p in path:
            status = svn_command('status', [p]).decode('utf-8')
            if status and status[0] == '?':
                svn_command('add', [p])

        svn_command('commit', ['-m', 'by bomb'] + path)
    except SVNError as e:
        logger.warn(e)


def svn_remove(path):
    verbose_svn_command('delete', path)
    svn_commit(path)


def svn_lock(path):
    verbose_svn_command('lock', ['-m', 'by bomb'] + path)


def svn_unlock(path):
    try:
        status = svn_command('status', path)
        if status.find('K') > -1:
            svn_command('unlock', path)
    except SVNError as e:
        logger.warn(e)
