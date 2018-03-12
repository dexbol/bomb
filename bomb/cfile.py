# coding=utf-8

import re
import logging
import os
import tempfile
import time
import random
from .utils import normalize_path, filename
from .compiler import compile_csjs
try:
    from react import jsx
except:
    jsx = None
try:
    from scss.compiler import Compiler as SCSSCompiler
except:
    SCSSCompiler = None

logger = logging.getLogger('bomb')

class CFile(object):
    '''config file object'''

    STALE_AGE = 8

    rdead = re.compile(r'^\s*/\*\s*@?dead\s*\*/\s*$')

    rmap = re.compile(r'''^\s*/\*\s*
                            @?map\s*=\s*(.+?)
                            \s*\*/ ''', re.VERBOSE)

    rnomap = re.compile(r'^\s*/\*\s*@?nomap\s*\*/\s*$')

    rbootstrap = re.compile(r'^\s*/\*\s*@?bootstrap\s*\*/\s*$', re.VERBOSE)

    rplaceholder = re.compile(r'^\s*/\*\s*@?placeholder\s*\*/\s*$')

    rversion = re.compile(r'''^\s*/\*\s*
                                @?version\s*=\s*(\d+)
                                \s*\*/\s*$''', re.VERBOSE)
    rnoversion = re.compile(r'^\s*/\*\s*@?noversion\s*\*/\s*$')

    rimport = re.compile(r'''^\s*\$?import\((.+)\)|
        ^\s*@import\s+url\((.+)\)
        ''', re.VERBOSE)

    rdepend = re.compile(r'^\s*\$?depend\((.+)\)')


    rfile = re.compile(r'\.js$|\.css$')

    def __init__(self, path, url_base=None, url_map=dict(), scss_root=None):
        self.path = path
        self.url_base = url_base if url_base != None\
            else (os.path.dirname(path) + os.sep\
            if os.path.dirname(path) != '' else '')
        self.url_map = url_map
        self.scss_root = scss_root

        self.filename, self.basename, self.extension = filename(path)

        self.dead = False
        self.frozen = False
        self.bootstrap = False
        self.placeholder = False
        self.stale_age = self.STALE_AGE
        self.noversion = False
        self.nomap = False

        self._map = ''
        self._version = -1
        self._uglyversion = self._base36encode(int(time.time() * 1000)) + \
                            str(random.randrange(0, 9999))
        self._file_depend = []
        self._tempfile = []

        # scan cfile attribute
        with open(path) as lines:
            for line in lines:
                matchobj = re.search(self.rdead, line)
                if matchobj:
                    self.dead = True
                    return

                matchobj = re.search(self.rbootstrap, line)
                if matchobj:
                    self.bootstrap = True

                matchobj = re.search(self.rplaceholder, line)
                if matchobj:
                    self.placeholder = True

                matchobj = re.search(self.rmap, line)
                if matchobj:
                    self._map = matchobj.group(1)

                matchobj = re.search(self.rnomap, line)
                if matchobj:
                    self.nomap = True

                matchobj = re.search(self.rversion, line)
                if matchobj:
                    self._version = int(matchobj.group(1))

                matchobj = re.search(self.rnoversion, line)
                if matchobj:
                    self.noversion = True

                matchobj = re.search(self.rdepend, line)
                if matchobj:
                    dependstr = matchobj.group(1)
                    self._file_depend.extend(dependstr.split(','))

        if self.version < 0:
            self.update_version()

    @property
    def version(self):
        return self._uglyversion if self.noversion else self._version

    @version.setter
    def version(self, version):
        if not self.noversion:
            content = []
            with open(self.path) as lines:
                for line in lines:
                    matchobj = re.search(self.rversion, line)
                    if not matchobj:
                        content.append(line)
            self._version = version
            content.insert(0, '/* @version=' + str(self._version) + ' */\n')
            with open(self.path, 'w') as handler:
                handler.write(''.join(content))

    @property
    def map(self):
        return '' if self.nomap else self._map

    @map.setter
    def map(self, newmap):
        if not self.nomap:
            new = []
            with open(self.path) as lines:
                for line in lines:
                    matchobj = re.search(self.rmap, line)
                    if not matchobj:
                        new.append(line)            

            new.insert(0, '/* @map = ' + newmap + ' */\n')
            with open(self.path, 'w') as handler:
                handler.write(''.join(new))
            self._map = newmap

    def update_version(self):
        if not self.noversion:
            self.version = self.version + 1

    def get_version_name(self, version=None):
        version = '_' + str(version if version !=None else self.version) + '.'
        return self.basename + version + self.extension

    def get_stale_name(self, stale_age=None):
        return self.get_version_name(self.version - \
            (stale_age or self.stale_age))

    def get_version_name_re(self):
        return re.compile(self.basename + '_' + r'([\dA-Z]+)' + r'\.' + \
            self.extension)

    def get_placeholder_re(self):
        name = self.basename + '\\.' + self.extension
        return re.compile(r'''(\/\*\s*_PLACEHOLDER_%s\s+START\s*\*\/)
            ([\s\S]*?)
            (\/\*\s*_PLACEHOLDER_%s\s+END\s*\*\/)
            ''' % (name, name), re.VERBOSE)

    def parse_content(self):
        if self.dead:
            return

        with open(self.path) as lines:
            for line in lines:
                importmatch = re.search(self.rimport, line)
                if importmatch:
                    path = importmatch.group(1) or importmatch.group(2)
                    path = re.sub('["\']', '', path)
                    path = self.parse_import_path(path)
                    for file_generator in self.import_file(path):
                        for l in file_generator:
                            yield l
                elif re.search(self.rdepend, line):
                    continue
                else:
                    yield line

    def parse_import_path(self, path):
        url_base = self.url_base
        url_map = self.url_map

        path = normalize_path(path)
        if path.find('!') >= 0 :
            path = path.split('!')
            prefix = path[0]
            if prefix in url_map:
                path = normalize_path(url_base + url_map[prefix] + path[1])
            else: 
                raise Exception('prefix not found ! (' + prefix + ')')    
        else:
            path = url_base + path

        if os.path.isfile(path):
            fileext = os.path.splitext(path)[1]
            if fileext == '.js' and jsx:
                with open(path) as handler:
                    content = handler.read()
                if self._match_jsx_notation(content):
                    temp = tempfile.mkstemp(fileext)
                    self._tempfile.append(temp)
                    jsx.transform(path, temp[1])
                    path = temp[1]
            if fileext == '.scss' and SCSSCompiler:
                compiler = SCSSCompiler(search_path=(self.scss_root,))
                temp = tempfile.mkstemp('.css')
                self._tempfile.append(temp)
                with open(path) as handler:
                    content = handler.read()
                content = compiler.compile_string(content)
                os.write(temp[0], content.encode('utf-8'))
                path = temp[1]

        return path

    def import_file(self, path):
        def _import(path):
            yield '\n'
            with open(path) as lines:
                for line in lines:
                    yield line

        if os.path.isdir(path):
            for (dirpath, dirnames, filenames) in os.walk(path):
                if '.svn' in dirnames:
                    dirnames.remove('.svn')
                for fname in filenames:
                    if fname.endswith('.js') or fname.endswith('.css'):
                        yield _import(os.path.join(dirpath, fname))
        else:
            yield _import(path)

    def update_map(self):
        reg = re.compile(r'''^\s*([A-Z]\w*)
            (?:\.add|\[['"]add['"]\])
            \((.*?)\s*,\s*function''', re.VERBOSE)
        rinternal = re.compile(r'^[\'"]?!')
        mods = []
        boom = None
        file_depend = self._file_depend
        dependstr = ''

        for line in self.parse_content():
            matchobj = re.match(reg, line)
            if matchobj:
                mods.append(matchobj.group(2))
                boom = matchobj.group(1)
        if not boom:
            return

        # strip module name begined with !
        mods = [m for m in mods if not re.match(rinternal, m)];
        if len(mods) > 0:
            modstr = ',\'mods\':[' + ','.join(mods) + ']'
        else:
            modstr = ''

        if len(file_depend) > 0 :
            dependstr = ",'requires':[" + ",".join(file_depend) + "]"

        version_name = self.get_version_name()
        mstr = '''%s['add']('%s',{'path':'%s'%s%s}); ''' % (boom,
            self.filename,
            version_name,
            modstr,
            dependstr
            );
        
        self.map = mstr    

    def dump(self, extension=[]):        
        content = []
        self.update_map()

        for line in self.parse_content():
            content.append(line)
        for line in extension:
            content.append(line)

        self._collect_garbage()

        return content

    def push(self, destination, extension=[]):
        content = self.dump(extension=extension)
        path = normalize_path(destination, self.get_version_name())

        with open(path, 'w', encoding='utf-8') as handler:
            handler.write(''.join(content))

        return path

    def update_referrer(self, referrer):
        pattern = self.get_placeholder_re() if self.placeholder else \
            self.get_version_name_re()
        referrer = normalize_path(referrer)

        with open(referrer) as handler:
            content = handler.read()

        if self.placeholder:
            logger.info('replace placeholder: ' + self.filename)
            spawn = ''.join(self.dump())
            temp = tempfile.mkstemp('.' + self.extension, text=True)
            handle, abspath = temp

            os.write(handle, spawn.encode('utf-8'))

            spawn = compile_csjs(abspath).decode('utf-8')
            content = re.sub(pattern, '\g<1>' + spawn + '\g<3>', content)
            os.close(handle)
            os.remove(abspath)
        else:
            content = re.sub(pattern, self.get_version_name(), content)

        with open(referrer, 'w', encoding='utf-8') as handler:
            handler.write(content)

    def _collect_garbage(self):
        for temp in self._tempfile:
            try:
                os.close(temp[0])
                os.remove(temp[1])
            except:
                continue

    def _match_jsx_notation(self, content):
        pattern = re.compile(r'\@jsx')
        result = re.search(pattern, content)
        return result

    def _base36encode(self, number, 
                            alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        if not isinstance(number, int):
            raise TypeError('number must be an integer')

        base36 = ''
        sign = ''

        if number < 0:
            sign = '-'
            number = -number

        if 0 <= number < len(alphabet):
            return sign + alphabet[number]

        while number != 0:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36
