# coding=utf-8

import os
import subprocess
import logging
from .utils import normalize_path

logger = logging.getLogger('bomb')

__all__ = ['compile_js', 'compile_css', 'compile_cfile']

JAR_PATH = normalize_path(os.path.dirname(__file__), '/jar/')


def compile_js(js, to, flag=[]):
	jarpath = normalize_path(JAR_PATH + 'closure-compiler.jar')
	args = ['java', '-jar', jarpath]
	args += ['--js', js]
	args += ['--js_output_file', to]
	args += ['--warning_level', 'QUIET']
	args += flag

	proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdoutdata, stderrdata = proc.communicate()
	if proc.returncode != 0:
		logger.warning(stderrdata)


def compile_css(css, to, flag=[]):
	jarpath = normalize_path(JAR_PATH + 'yuicompressor.jar')
	args = ['java', '-jar', jarpath, css]
	args += ['--type', 'css']
	args += ['--line-break', '86']
	args += ['--charset', 'utf-8']
	args += ['-o', to]
	args += flag
	
	proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdoutdata, stderrdata = proc.communicate()
	if proc.returncode != 0:
		logger.warning(stderrdata)


def compile_cfile(cfile, to, flag=[]):
	if cfile.endswith('.js'):
		compile_js(cfile, to, flag=flag)

	elif cfile.endswith('.css'):
		compile_css(cfile, to, flag=flag)