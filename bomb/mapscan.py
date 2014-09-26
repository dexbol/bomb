# coding = utf-8

import os
import argparse
import logging
import re


logger = logging.getLogger('bomb')

MAP_PREPARE = '''/* Created automaticly by bomb. 
*** Please do not edit. ***  
*/
;(function() {
	var scripts;
	var thescript;
	var path;
	var base;
	var i = 0;
	var reg = /^(.*\/)\w+\.js$/;

	if (document.currentScript) {
		thescript = document.currentScript;

	} else {
		scripts = document.getElementsByTagName('script');
		for (; i < scripts.length; i++) {
			if (scripts[i].readyState == 'interactive') {
				thescript = scripts[i];
				break;
			}
		}
		if (!thescript) {
			thescript = scripts[scripts.length - 1];
		}
	}

    path = thescript.src;
    base = path.match(reg)[1];
    %s.config('base', base);
})(); '''


DEFAULT_REQUIRES = "'jquery'"

BOOM = 'CN6'

raddModule = re.compile('''^\s*([A-Z0-9]+)\.add\(
	\s*['"]
	(?:\w*?(?=!)!?)?([-_\.\w]+) # module name maybe prefix by !
	['"] 
	\s*,\s*function
	''', re.VERBOSE)

rrequireModuleStart = re.compile('''requires\s*\:\s*\[([^\]]+)(\])?''', re.VERBOSE)
rrequireModuleEnd = re.compile('''^\s*([^\]]+)\]\}\)\s*\;?\s*$''', re.VERBOSE)


def _isJsFile(ref):
	return ref.endswith('.js')


def _normalizeUrl(path):
	return '/'.join(path.split(os.sep))


def _normalizeFileName(path):
	'''normalize file name . trim version number, dash and "-min" suffix
	 e.g. jquery-1.7.0-min.js to jquery'''

	filename = os.path.split(path)[1]
	pattern = re.compile('[^\d]+')
	matchObj = re.match(pattern, filename)
	if matchObj:
		filename = matchObj.group(0)
		if filename.endswith('.js'):
			filename = filename[0:-3]
		if filename.endswith('-'):
			filename = filename[0:-1]
	return filename


def _expandDirectories(path):
	result = []
	for (directory, subdirs, filenames) in os.walk(path):
		for filename in filenames:
			if _isJsFile(filename):
				result.append(os.path.join(directory, filename))
	return result


class _ModuleInfo(object):
	def __init__(self, modulename, modulerequire, path):
		self.modulename = modulename
		self.modulerequire = modulerequire
		self.path = path

	def __str__(self):
		if self.modulerequire:
			self.modulerequire = ', requires: [%s]' % self.modulerequire
		return '''%s.add('%s', {path: '%s'%s});''' % (BOOM, self.modulename,
			 self.path, self.modulerequire)


def _buildMapFormFile(files, basepath):
	result = []
	for f in files:
		result.extend(_scanFileContent(f, basepath))
	return result


def _scanFileContent(file, basepath):
	result = []
	notFountModule = True
	mutiLineRequires = False
	cream = ''

	with open(file, 'r') as handler:
		for line in handler:
			matchObj = re.search(raddModule, line)
			if matchObj:
				notFountModule = False
				cream += '@' + matchObj.group(2)
				continue

			matchObj = re.search(rrequireModuleStart, line)
			if matchObj:
				cream += '%' + matchObj.group(1)
				if matchObj.group(2) != ']':
					mutiLineRequires = True
				continue

			if mutiLineRequires:
				matchObj = re.search(rrequireModuleEnd, line)
				if matchObj:
					cream += matchObj.group(1)
					mutiLineRequires = False
				else:
					cream += line.strip()

	# we don't find any boom module so use the file name
	if notFountModule:
		cream = '@' + _normalizeFileName(file)
		# guess is it a jquery plugin
		if cream != '@jquery' and 'jquery' in cream:
			cream += '%' + '\'jquery\''
	modulepath = os.path.relpath(file, basepath)
	modulepath = _normalizeUrl(modulepath)
	cream = cream.split('@')
	cream.pop(0)

	for module in cream:
		exploded = module.split('%')
		len(exploded) == 1 and exploded.append('')
		modulename, modulerequire = exploded
		result.append(_ModuleInfo(modulename, modulerequire, modulepath))
		logger.info(modulename + ' - ' + modulepath)

	return result


def write(path, dest='map.js', boom=BOOM):
	if not os.path.exists(path):
		logger.warning('the path is not exist')
		return

	dest_path = os.path.join(path, dest)

	try:
		os.remove(dest_path)
	except:
		pass

	files = _expandDirectories(path)
	maps = _buildMapFormFile(files, path)
	with open(dest_path, 'w') as handler:
		handler.write(MAP_PREPARE % boom)
		for m in maps:
			handler.write('\n' + str(m))
