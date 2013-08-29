# coding=utf-8

import os
import sys
import subprocess
from distutils.core import setup
from distutils.command.install_scripts import install_scripts


root_dir = os.path.dirname(__file__)
root_dir_unix = '/'.join(root_dir.split(os.sep)) or '.'


def check_command(command):
	try:
		subprocess.check_call(command, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
	except subprocess.CalledProcessError:
		return False

	return True

print 'Check java runtime environment:'
if check_command(['java', '-version']):
    print 'JRE is already installed'
else:
    print '*** Not found JRE in your computer. Please ensure that JRE is'
    print 'installed. If you already installed, but you still see this'
    print 'error message, please refer http://java.com/en/download/help/path.xml'
    sys.exit('***Install Failed***')


print 'Check SVN client command-line tools:'
if check_command(['svn', '--version']):
    print 'SVN can work anytime.'
else:
    print '*** Not found SVN client tools, please install it.'
    print 'You can download it from'
    print 'http://subversion.apache.org/packages.html'
    print 'I advise you download CollabNet on windows.'
    sys.exit('***Install Failed***')


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
                print ('Created: %s' % bat_path)
            except:
                print ('ERROR: Unable to create %s: %s' % (bat_path, err))



try:
	with open(root_dir + os.sep + 'README.md') as handler:
		long_description = handler.read()
except:
	long_description = ''

setup(
	name='bomb',
	version='0.1.5',
	description='Web frond-end publish tools',
	long_description=long_description,
	author='dexbol',
	author_email='dexbolg@gmail.com',
	url='',
	packages=['bomb'],
	package_dir={'': root_dir_unix},
	package_data={'bomb': ['jar/*.jar']},
	scripts=[root_dir_unix + '/bin/bomb'],
	cmdclass={'install_scripts':my_install_scripts}
	)
