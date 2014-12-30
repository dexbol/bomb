# coding=utf-8

import os
import subprocess
import logging
from .utils import normalize_path

logger = logging.getLogger('bomb')

__all__ = ['compile_js', 'compile_css', 'compile_csjs']

JAR_PATH = normalize_path(os.path.dirname(__file__), '/jar/')


def compile_js(js, to=None, flag=[]):
    jarpath = normalize_path(JAR_PATH + 'closure-compiler.jar')
    args = ['java', '-jar', jarpath]
    args += ['--js', js]
    args += ['--warning_level', 'QUIET']

    if to:
        args += ['--js_output_file', to]

    args += flag

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()
    if proc.returncode != 0:
        logger.warning(stderrdata)
    if not to:
        return stdoutdata


def compile_css(css, to=None, flag=[]):
    jarpath = normalize_path(JAR_PATH + 'yuicompressor.jar')
    args = ['java', '-jar', jarpath, css]
    args += ['--type', 'css']
    args += ['--line-break', '86']
    args += ['--charset', 'utf-8']

    if to:
        args += ['-o', to]

    args += flag
    
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdoutdata, stderrdata = proc.communicate()
    if proc.returncode != 0:
        logger.warning(stderrdata)
    if not to:
        return stdoutdata


def compile_csjs(srcfile, to=None, flag=[]):
    if srcfile.endswith('.js'):
        result = compile_js(srcfile, to, flag=flag)

    elif srcfile.endswith('.css'):
        result = compile_css(srcfile, to, flag=flag)

    return result