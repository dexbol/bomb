# coding=utf-8


import sys 
import re 
import os 
import json
import logging
import subprocess
import argparse
import shutil


# try:
# 	import pysvn
# except ImportError:
# 	pysvn = None


logging.basicConfig(format=('>>' + ' %(message)s'), 
					level=logging.DEBUG)


WARNING_NO_PYSVN = 'you need install pysvn, read README for detail.'

SCRIPT_PATH = 'E:/6rooms/'


# def svn_update(path):
# 	if not pysvn:
# 		logging.warning(WARNING_NO_PYSVN)
# 		return
# 	for p in path:
# 		logging.info('svn update: ' + p)
# 	pysvn.Client().update(path, recurse=True)


# def svn_commit(path):
# 	if not pysvn:
# 		logging.warning(WARNING_NO_PYSVN)
# 		return				
# 	client = pysvn.Client()
# 	for p in path:
# 		logging.info('svn commit: ' + p)
# 		if not client.info(p):
# 			client.add(p)
# 	client.checkin(path, 'by builder', recurse=True)


# def svn_remove(path):
# 	if not pysvn:
# 		logging.warning(WARNING_NO_PYSVN)
# 		return
# 	for p in path:
# 		logging.info('svn delete : ' + p)
# 	client = pysvn.Client()
# 	client.remove(path)
# 	client.checkin(path, 'by builder')

def svn_command(command, args):
	exe = normally_path('D:/Program Files/SlikSvn/bin/svn.exe')
	lines = [exe, command]
	lines += args
	proc = subprocess.Popen(lines, stdout=subprocess.PIPE)
	stdoutdata, unused_stderrdata = proc.communicate()
	if proc.returncode != 0:
		return

	return stdoutdata


def svn_update(path):
	svn_command('update', path)


def svn_commit(path):
	for p in path:
		status = svn_command('status', [p])
		if status and status[0] == '?':
			svn_command('add', [p])

	svn_command('commit', ['-m', 'by boombuilder.py'] + path)


def svn_remove(path):
	svn_command('delete', 
		['-m', 'deleted by boombuilder.py'] + path)


def compile_js(js, to, flag=[]):
	if __name__ == '__main__':
		jarpath = sys.path[0]
	else:
		jarpath = sys.path[1]
	jarpath = normally_path(jarpath + '/closure-compiler.jar')
	args = ['java', '-jar', jarpath]
	args += ['--js', js]
	args += ['--js_output_file', to]
	args += ['--warning_level', 'QUIET']
	args += flag
	retcode = subprocess.call(args)
	if retcode != 0:
		logging.warning('Compile js fail : ' + js)


def compile_css(css, to, flag=[]):
	if __name__ == '__main__':
		jarpath = sys.path[0]
	else:
		jarpath = sys.path[1]
	jarpath = normally_path(jarpath + '/yuicompressor.jar')
	args = ['java', '-jar', jarpath, css]
	args += ['--type', 'css']
	args += ['--line-break', '86']
	args += ['--charset', 'utf-8']
	args += ['-o', to]
	args += flag
	retcode = subprocess.call(args)
	if retcode != 0:
		logging.warning('Compress css fail : ' + css)	


def normally_path(*path):
	path = ''.join(path)
	path = os.sep.join(re.split(r'[\/]', path))
	exploded = os.path.split(path)
	basename = exploded[1]

	if basename == '':
		basename = os.sep
	else:
		basename = os.sep + basename

	return os.path.normpath(exploded[0]) + basename


def filename(file):
	pattern = re.compile(r'[/\\]([\w_-]+\.\w+$)')
	matchObj = re.search(pattern, file)
	if matchObj:
		filename = matchObj.group(1)
	else:
		filename = file
	pattern = re.compile(r'^(.+)\.(.+)$')
	matchObj = re.search(pattern, filename)
	if matchObj:
		# (filename, name, extend name)
		return (filename, matchObj.group(1), matchObj.group(2))
	else:
		return (filename)


class CFile:
	'''config file object'''

	rdead = re.compile(r'^\s*/\*\s*dead\s*\*/\s*$')

	rmap = re.compile(r'''^\s*/\*\s*
							map\s*=\s*(.+)
							\s*\*/ ''', re.VERBOSE)

	rbootstrap = re.compile(r'^\s*/\*\s*bootstrap\s*\*/\s*$', re.VERBOSE)

	rversion = re.compile(r'''^\s*/\*\s*
								version\s*=\s*(\d+)
								\s*\*/\s*$''', re.VERBOSE)

	def __init__(self, path, url_base='', url_map=dict()):
		self.path = path
		self.url_base = url_base
		self.url_map = url_map
		self.froze = False
		self.dead = False
		self.map = ''
		self.bootstrap = False
		self.version = -1
		self.parsed_content = []

		handler = open(path)
		lines = handler.readlines()

		for line in lines:
			matchobj = re.search(self.rdead, line)
			if matchobj:
				self.dead = True
				return

			matchobj = re.search(self.rbootstrap, line)
			if matchobj:
				self.bootstrap = True

			matchobj = re.search(self.rmap, line)
			if matchobj:
				self.map = matchobj.group(1)

			matchobj = re.search(self.rversion, line)
			if matchobj:
				self.version = int(matchobj.group(1))

		handler.close()

		if self.version < 0:
			self.update_version()

	def get_version(self):
		return self.version

	def update_version(self):
		content = []
		with open(self.path) as lines:
			for line in lines:
				matchobj = re.search(self.rversion, line)
				if not matchobj:
					content.append(line)
		self.version += 1
		content.insert(0, '/* version=' + str(self.version) + ' */\n')
		handler = open(self.path, 'w')
		handler.write(''.join(content))
		handler.close()

	def get_version_name(self):
		cfile_name = filename(self.path)[0]
		cfile_name_tuple = filename(cfile_name)
		version = '_' + str(self.get_version()) + '.'
		cfile_version_name = '%s%s%s' % (cfile_name_tuple[1], version, 
			cfile_name_tuple[2])
		return cfile_version_name	

	def get_version_name_re(self):
		fname = filename(self.path)
		return re.compile(fname[1] + '_' + r'(\d+)' + r'\.' + fname[2])	

	def get_map(self):
		return self.map
	
	def update_map(self, newmap):
		handler = open(self.path)
		lines = handler.readlines()
		new = []

		for line in lines:
			matchobj = re.search(self.rmap, line)
			if not matchobj:
				new.append(line)

		new.insert(0, '/* map = ' + newmap + ' */\n')
		handler = open(self.path, 'w')
		handler.write(''.join(new))
		handler.close()
		self.map = newmap

	def get_parsed(self):
		return self.parsed_content

	def extend_parsed(self, extra=[]):
		self.parsed_content = self.parsed_content + extra

	def parse(self):
		if self.dead:
			return

		parsed_content = []
		url_base = self.url_base
		url_map = self.url_map

		rimport = re.compile(r'''^\s*\$?import\((.+)\)|
			^\s*@import\s+url\((.+)\)
			''', re.VERBOSE)
		rdepend = re.compile(r'^\s*\$?depend\((.+)\)')
		filetype = filename(self.path)[2]
		handler = open(self.path, 'r')
		lines = handler.readlines()
		depend = []

		for line in lines:
			importmatch=re.search(rimport,line)
			dependmatch=re.search(rdepend,line)
			if importmatch:
				path = importmatch.group(1) or importmatch.group(2)
				path = re.sub('["\']', '', path)
				path = self.import_path(path)
				self.import_file(path, parsed_content, filetype)
			elif dependmatch:
				s = dependmatch.group(1)
				s = s.split(',')
				depend.extend(s)
			else:
				parsed_content.append(line)

		self.parsed_content = parsed_content
		self._file_depend = depend
		if not self.bootstrap:
			self.scan_map()
		handler.close()

	def import_path(self, path):
		url_base = self.url_base
		url_map = self.url_map
		path = normally_path(path)

		if path.find('!') < 0 :
			return url_base + path
		
		path = path.split('!')
		prefix = path[0]
		if prefix in url_map:
			return normally_path(url_base + url_map[prefix] + path[1])
		else: 
			raise Exception('prefix not found !')		

	def import_file(self, path, parsed_content, filetype):
		rdirectory = re.compile(r'[/\\]$')
		rfile = re.compile(r'\.js$|\.css$')

		if re.search(rdirectory, path):
			for (directory, subdirs, filenames) in os.walk(path):
				for fname in filenames:
					self.import_file(os.sep.join([directory, fname]), 
						parsed_content, filetype)
		else:
			extend_name = filename(path)[2]
			if extend_name == filetype:
				with open(path) as thisfile:
					for line in thisfile:
						parsed_content.append(line)
				parsed_content.append('\n\t')

	def scan_map(self):
		content = self.parsed_content
		reg = re.compile(r'^\s*([A-Z]\w*)\.add\((.*?)\s*,\s*function')
		rinternal = re.compile(r'^[\'"]?!')
		mods = []
		boom = None
		file_depend = self._file_depend
		dependstr = ''
		for line in content:
			matchobj = re.match(reg, line);
			if matchobj:
				mods.append(matchobj.group(2));
				boom = matchobj.group(1);
		if not boom:
			return ;

		mds = [];
		for mod in mods :
			mds.extend(mod.split(','));

		# module name begined with !
		mods = [m for m in mds if not re.match(rinternal,m)];
		if len(mods) > 0:
			modstr = ',\'mods\':[' + ','.join(mods) + ']';
		else:
			modstr = '';

		if len(file_depend) > 0 :
			dependstr = ",'requires':[" + ",".join(file_depend) + "]"

		cfile_name = filename(self.path)[0]
		cfile_version_name = self.get_version_name()
		mstr = '''%s['add']('%s',{'path':'%s'%s%s}); ''' % (boom,
			cfile_name,
			cfile_version_name,
			modstr,
			dependstr
			);
		
		self.update_map(mstr)		

	def push(self, destination):
		handler = open(normally_path(destination), 'w')
		for line in self.parsed_content:
			handler.write(line)
		handler.close()

	def update_referrer(self, referrer, pattern=None, repl=None):
		pattern = pattern or self.get_version_name_re()
		repl = repl or self.get_version_name()
		repl = repl.encode('utf-8')
		referrer = normally_path(referrer)
		handler = open(referrer)
		content = handler.read()

		content = re.sub(pattern, repl, content)

		handler = open(referrer, 'w')
		handler.write(content)
		handler.close()


class Config:
	def __init__(self):
		pass

	def load(self, file):
		try:
			handler = open(file)
		except IOError:
			return

		lines = handler.readlines()
		rcomment = re.compile(r'^\s*\/\/')
		result = []
		for line in lines:
			if not re.search(rcomment, line):
				result.append(line)
		config = json.loads(''.join(result))
		try:
			self._config.update(config)
		except AttributeError:
			self._config = config
		logging.info('Load config file : ' + file)

	def get(self, key):
		return self._config[key]

	def set(self, key, value):
		try:
			self._config[key] = value
		except AttributeError:
			self._config = {}
			self._config[key] = value	


class Builder:
	def __init__(self, buildpath=False, args=None):
		self.buildpath = buildpath or ''
		self.args = args
		self.tempath = ''
		self.cfile = dict()
		self.template = []
		self._config = dict()
		self._updateversion = True
		self._garbage = []
		self._parsed = []
		self._compiled = []
		self._storepath = ''
		self.config = Config()

		if not self.buildpath.endswith(os.sep):
			self.buildpath += os.sep

	def fullpath(self, path):
		return normally_path(self.buildpath + path)

	def argument(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-v', help='do not update version', 
			action='store_true')
		parser.add_argument('-d', help='debug mode will keep paresed file', 
			action='store_true')
		parser.add_argument('--list', help='show all config file', 
			action='store_true')
		parser.add_argument('--select', help='select cfile', action='store')

		if self.args == None:
			result = parser.parse_args()
		else:
			result = parser.parse_args(self.args)
		lineargs = vars(result)
		return lineargs

	def list_cfile(self):
		cfile = self.cfile
		index = 0
		for key in cfile.keys():
			cf = cfile[key]
			cf.index = index
			logging.info(str(index) + '. ' + key) 
			index += 1

	def scan_cfile(self, path):
		files = os.listdir(path)
		
		for f in files:
			self.add_cfile([normally_path(path + '/' + f)])			

	def add_cfile(self, paths=[]):
		cfile = self.cfile

		for path in paths:
			fname = filename(path)[0]
			cf = CFile(normally_path(path), self.buildpath, 
				self.config.get('prefix_path'))
			if cf.dead:
				continue
			cfile[fname] = cf

	def filter_cfile(self, selected):
		self.list_cfile()
		cfile = self.cfile
		selected = selected.split(',')
		filters = []
		hasjs = False

		for n in selected:
			n = int(n)
			for key in cfile.keys():
				cf = cfile[key]
				if cf.index == n:
					filters.append(key)

		for key in cfile.keys():
			cf = cfile[key]
			if key in filters:
				cf.froze = False
			else:
				cf.froze = True

		logging.info('you selected ' + str(filters))

	def parse(self):
		cfile = self.cfile
		update_version = self._updateversion
		bootstrap = False
		hasjs = False
		maps = []

		for key in cfile.keys():
			cf = cfile[key]
			if cf.froze:
				maps.append(cf.get_map())
				continue
			if filename(cf.path)[2] == 'js':
				hasjs = True
			if cf.bootstrap:
				continue
			if update_version:
				cf.update_version()
			cf.parse()
			maps.append(cf.get_map())
			self.push_parsed_content(cf)

		if hasjs:
			for key in cfile.keys():
				cf = cfile[key]
				if cf.bootstrap:
					update_version and cf.update_version()
					cf.parse()
					cf.extend_parsed(maps)
					self.push_parsed_content(cf)					

	def push_parsed_content(self, cfile):
		version_name = cfile.get_version_name()
		temp_path = self.tempath
		destination = temp_path + version_name
		cfile.push(destination)
		self._parsed.append(destination)

	def normally_template(self):
		template = self.config.get('template')
		template_list = []
		for temp in template:
			temp = self.fullpath(temp)
			template_list.append(temp)
		self.template = template_list

	def update_template(self):
		for temp in self.template:
			handler = open(temp)
			content = handler.read()

			for key in self.cfile.keys():
				cf = self.cfile[key]
				version_name = cf.get_version_name()
				version_name = version_name.encode('utf-8')
				version_reg = cf.get_version_name_re()
				content = re.sub(version_reg, version_name, content)

			handler.close()
			handler = open(temp, 'w')
			handler.write(content)
			handler.close()

	def svn_update(self):
		svn_update(self.template)
		svn_update([self.buildpath])
		svn_update(self._compiled)

	def svn_commit(self):
		svn_commit(self.template)
		svn_commit([self.buildpath])
		svn_commit(self._compiled)

	def svn_remove(self):
		svn_remove(self._garbage)

	def del_temp_dir(self):
		self.tempath = self.fullpath('temp/')
		try:
			shutil.rmtree(self.tempath)
		except:
			pass

	def create_temp_dir(self):
		self.del_temp_dir()
		os.makedirs(self.tempath)

	def compile(self):
		store_dir = self._storepath

		for f in self._parsed:
			filetype = filename(f)[2]
			destination = store_dir + filename(f)[0]
			logging.info('Compiling ... ' + destination)
			self._compiled.append(destination)

			if filetype == 'css':
				compile_css(f, destination)
			if filetype == 'js':
				compile_js(f, destination)

	def collect_garbage(self):
		collection = []
		for key in self.cfile.keys():
			cf = self.cfile[key]
			version = cf.get_version()
			version = version - 8
			fn_tuple = filename(cf.path)
			fn = fn_tuple[1] + '_' + str(version) + '.' + fn_tuple[2]
			path = self._storepath + fn

			try:
				os.remove(path)
				collection.append(path)
			except:
				pass
		self._garbage = collection

	def make(self):
		self.config.load(self.fullpath('config.json'))
		self.config.load(self.fullpath('config_user.json'))

		self.scan_cfile(self.fullpath(self.config.get('cfile_path')))
		self.normally_template()
		lineargs = self.argument()


		if lineargs['list']:
			self.list_cfile()
			return

		self.svn_update()

		self.create_temp_dir()

		self._storepath = self.fullpath(self.config.get('store'))


		if lineargs['select']:
			self.filter_cfile(lineargs['select'])

		if lineargs['v']:
			self._updateversion = False
			
		self.parse()

		self.update_template()

		self.compile()

		self.svn_commit()

		self.collect_garbage()

		self.svn_remove()

		if not lineargs['d']:
			self.del_temp_dir()


'''
NOTE: 

- 支持import文件夹下所有css或js模块文件

'''