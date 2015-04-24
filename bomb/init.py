# coding=utf-8

import os
import logging
from .utils import normalize_path


CONFIG_TEMPLATE = '''{

    // cfile path or directory, empty string means the directory that 
    // config.json in.
    "cfile": [""],

    // path that refer to compiled cfile , normmaly it is a html or tpl file
    "referrer": [""],

    // path that contain compiled cfile
    "store": "",

    // the key value is prefix path consistently, this supply a convenient way
    // to import other file in cfile. e.g. a prefix path pair like this
    // {'lib': '/srv/www/html/csjs/lib'}, than in cfile you can use
    // `$import("lib!jquery.js")` to import /srv/www/html/csjs/lib/jquery.js 
    "prefix_path": {},

    "debug": false,

    "scss_root": "",

    "ftp_ip": "",

    "ftp_port": "",

    "ftp_username": "",

    "ftp_password": "",

    "ftp_root": ""
}
'''


logger = logging.getLogger('bomb')

def init_config(path):
    path = normalize_path(path + '/config.json')
    if os.path.exists(path):
        logger.info('config.json is exsits')
    else:
        with open(path, 'w') as handler:
            handler.write(CONFIG_TEMPLATE)
        return path

