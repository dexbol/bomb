# coding=utf-8

import os
import sys
import subprocess
from distutils.core import setup
from distutils.command.install_scripts import install_scripts
try:
    import py2exe
except:
    py2exe = None


class my_install_scripts(install_scripts):
    def run(self):
        install_scripts.run(self)

        if sys.platform == 'win32':
            try:
                script_dir = os.path.join(sys.prefix, 'Scripts')
                script_path = os.path.join(script_dir, 'bomb')
                bat_str = '@"%s" "%s" %%*' % (sys.executable, script_path)
                bat_path = os.path.join(self.install_dir, 'bomb.bat')
                with open(bat_path, 'w') as handler:
                    handler.write(bat_str)
                print(('Created: %s' % bat_path))
            except:
                print(('ERROR: Unable to create %s: %s' % (bat_path, err)))


try:
    with open(root_dir + os.sep + 'README.md') as handler:
        long_description = handler.read()
except:
    long_description = ''


setup(
    name='bomb',
    version='1.0.1',
    description='Web frond-end publish tools',
    long_description=long_description,
    author='dexbol',
    author_email='dexbolg@gmail.com',
    url='https://github.com/dexbol/bomb',
    packages=['bomb'],
    package_data={'bomb': ['jar/*.jar']},
    include_package_data=True,
    scripts=['bin/bomb'],
    cmdclass={'install_scripts':my_install_scripts},
    console=['bin/bomb'],
    options={
        "py2exe": {
            "skip_archive": True
        }
    }
)
