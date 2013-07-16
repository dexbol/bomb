# coding = utf-8

import os
import argparse
import logging
import re


MAP_PREPARE = '''/*Created automaticly by boomap.py */
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
rrequireModuleEnd = re.compile('''^\s*([^\]]+)\]\}\)\;?$''', re.VERBOSE)

logging.basicConfig(format='boomap.py>> %(message)s', level=logging.INFO)


def isJsFile(ref):
	return ref.endswith('.js')


def normalizeUrl(path):
	return '/'.join(path.split(os.sep))


def normalizeFileName(path):
	'''normalize file name . trim version number, dash and "-min" suffix
	 e.g. jquery-1.7.0-min.js to jquery'''

	fragment = re.split(r'[/\\]', path)
	filename = fragment[-1]
	pattern = re.compile('[^\d]+')
	matchObj = re.match(pattern, filename)
	if matchObj:
		filename = matchObj.group(0)
		if filename.endswith('.js'):
			filename = filename[0:-3]
		if filename.endswith('-'):
			filename = filename[0:-1]
	return filename


def expandDirectories(path):
	result = []
	for (directory, subdirs, filenames) in os.walk(path):
		for filename in filenames:
			if isJsFile(filename):
				result.append(os.path.join(directory, filename))
	return result


class ModuleInfo(object):
	def __init__(self, modulename, modulerequire, path):
		self.modulename = modulename
		self.modulerequire = modulerequire
		self.path = path
	def __str__(self):
		if self.modulerequire:
			self.modulerequire = ', requires: [%s]' % self.modulerequire
		return '''%s.add('%s', {path: '%s'%s})''' % (BOOM, self.modulename,
			 self.path, self.modulerequire)


def buildMapFormFile(files, basepath):
	result = []
	for f in files:
		result.extend(scanFileContent(f, basepath))
	return result


def scanFileContent(file,basepath):
	handler = open(file, 'r')
	lines = handler.readlines()
	result = []
	notFountModule = True
	mutiLineRequires = False
	cream = ''
	for line in lines:
		matchObj = re.search(raddModule, line)
		if matchObj:
			notFountModule = False
			cream += '@' + matchObj.group(2)
		matchObj = re.search(rrequireModuleStart, line)
		if matchObj:
			cream += '%' + matchObj.group(1)
			if matchObj.group(2) != ']':
				mutiLineRequires = True	
		elif mutiLineRequires:
			matchObj = re.search(rrequireModuleEnd, line)
			if matchObj:
				cream += matchObj.group(1)
				mutiLineRequires = False
			else:
				cream += line.strip()
	# we don't find any boom module use the file name
	if notFountModule:
		cream = '@' + normalizeFileName(file)
		# guess is it a jquery plugin
		if cream != '@jquery' and 'jquery' in cream:
			cream += '%' + '\'jquery\''
	modulepath = os.path.relpath(file, basepath)
	modulepath = normalizeUrl(modulepath)
	cream = cream.split('@')
	cream.pop(0)
	for module in cream:
		kv = module.split('%')
		len(kv) is 1 and kv.append('')
		result.append(ModuleInfo(kv[0], kv[1], modulepath))
		logging.info(kv[0] + ' - ' + modulepath)
	return result


def main():
	global BOOM 
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--path', dest='path', action='store', help='path to parse')
	parser.add_argument('-d', '--dest', dest='dest', action='store', help='dest file name')
	parser.add_argument('-b', '--boom', dest='boom', action='store', help='global object name, \
		defalut is CN6')

	args = vars(parser.parse_args())
	dest = args['dest'] or 'map.js'
	path = args['path']
	boom = args['boom'] or BOOM

	if not path:
		logging.info('argument required, -h see detail')
		return

	if not os.path.exists(path):
		logging.info('the path is not exist')
		return
	BOOM = boom
	dest_path = os.path.join(args['path'], dest)
	try:
		os.remove(dest_path)
	except:
		pass
	files = expandDirectories(path)
	maps = buildMapFormFile(files, path)
	handler = open(dest_path, 'w')
	prepare = MAP_PREPARE % BOOM
	handler.write(prepare)
	for m in maps:
		handler.write('\n' + str(m))
	handler.close()

	

if __name__ == '__main__':
	main()