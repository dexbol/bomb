# coding=utf-8

import subprocess
import logging

logger = logging.getLogger('bomb')

__all__ = ['svn_command', 'svn_update', 'svn_commit', 'svn_remove',
	'svn_lock', 'svn_unlock']

def svn_command(command, args):
	lines = ['svn', command]
	lines += args

	proc = subprocess.Popen(lines, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdoutdata, stderrdata = proc.communicate()
	if proc.returncode != 0:
		logger.warning(stderrdata)

	return stdoutdata


def svn_update(path):
	svn_command('update', path)


def svn_commit(path):
	for p in path:
		status = svn_command('status', [p])
		if status and status[0] == '?':
			svn_command('add', [p])

	svn_command('commit', ['-m', 'by bomb'] + path)


def svn_remove(path):
	svn_command('delete', path)
	svn_commit(path)


def svn_lock(path):
	svn_command('lock', ['-m', 'by bomb'] + path)


def svn_unlock(path):
	status = svn_command('status', path)
	if status.find('K') > -1:
		svn_command('unlock', path)