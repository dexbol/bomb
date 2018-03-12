# coding=utf-8

import env
import logging
import re
import os
import shutil
import unittest
from bomb.cfile import CFile
from bomb.utils import normalize_path
from env import root_path, test_path

CFILE_CONTENT = '''
/* @version = 100 */
/* @map = foo */

depend('jquery.js')
$import('module_1.js')
$import('root!module_2.js)
$import('../lib/');
'''

CFILE_CSS_CONTENT = ''' 
@import url(a.css);
@import url('b.css');
@import url("c.css");
'''

CFILE_HOLDER_CONTENT = '''
/* @placeholder */
@import url(a.css);
@import url(b.css);
@import url(c.css);
'''

MODULE_1_CONTENT = '''
CN6.add('lucy',   function() {
    // code
});

CN6['add']('alice', function(C) {
    //code
})
'''

MODULE_2_CONTENT = '''
    CN6.add('jack', function(C) {

        // code
        });
'''

MODULE_3_CONTENT = '''
CN6["add"]('dexter', function() {

    })
'''

MODULE_4_CONTENT = '''
CN6.add('priscilla', function() {

    });
'''

CSS_A_CONTENT = '''
.a {color: red;}
'''

CSS_B_CONTENT = '''
.b {color: blue;}
'''

CSS_C_CONTENT = '''
.c {color: yellow;}
'''

REFERRER_CONTENT = '''
<title>中文</title>
<script src="//domain/path/static/cfile_0.js"></script>
<style>
/* _PLACEHOLDER_cfile_holder.css START */
some code
/* _PLACEHOLDER_cfile_holder.css END */
</style>
'''

class TestCFile(unittest.TestCase):

    def setUp(self):
        try:
            os.mkdir(root_path + 'lib')
        except:
            pass

        try:
            with open(test_path + 'module_1.js', 'w') as handler:
                handler.write(MODULE_1_CONTENT)
        except:
            pass

        try:
            with open(root_path + 'module_2.js', 'w') as handler:
                handler.write(MODULE_2_CONTENT)
        except:
            pass

        try:
            with open(root_path + 'lib/module_3.js', 'w') as handler:
                handler.write(MODULE_3_CONTENT)
        except:
            pass

        try:
            with open(root_path + 'lib/module_4.js', 'w') as handler:
                handler.write(MODULE_4_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'cfile.js', 'w') as handler:
                handler.write(CFILE_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'referrer.txt', 'w') as handler:
                handler.write(REFERRER_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'cfile.css', 'w') as handler:
                handler.write(CFILE_CSS_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'a.css', 'w') as handler:
                handler.write(CSS_A_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'b.css', 'w') as handler:
                handler.write(CSS_B_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'c.css', 'w') as handler:
                handler.write(CSS_C_CONTENT)
        except:
            pass

        try:
            with open(test_path + 'cfile_holder.css', 'w') as handler:
                handler.write(CFILE_HOLDER_CONTENT)
        except:
            pass

        self.cfile = CFile(test_path + 'cfile.js', url_map={
            'root': normalize_path('../')
            })

    def tearDown(self):
        try:
            os.remove(test_path + 'module_1.js')
        except:
            pass

        try:
            os.remove(root_path + 'module_2.js')
        except:
            pass

        try:
            os.remove(test_path + 'cfile.js')
        except:
            pass

        try:
            os.remove(test_path + 'referrer.txt')
        except:
            pass

        try:
            os.remove(test_path + self.cfile.get_version_name())
        except:
            pass

        try:
            shutil.rmtree(root_path + 'lib')
        except:
            pass

        try:
            os.remove(test_path + 'a.css')
        except:
            pass

        try:
            os.remove(test_path + 'b.css')
        except:
            pass

        try:
            os.remove(test_path + 'c.css')
        except:
            pass

        try:
            os.remove(test_path + 'cfile_holder.css')
        except:
            pass

        try:
            os.remove(test_path + 'cfile.css')
        except:
            pass

    def test_attribut(self):
        self.assertEqual(self.cfile.version, 100)
        self.assertEqual(self.cfile.map, 'foo')

    def test_property(self):
        self.cfile.version = 88
        self.cfile.map = 'bar'

        version = 0
        mapstr = ''

        with open(self.cfile.path) as lines:
            for line in lines:
                matchobj = re.search(self.cfile.rversion, line)
                if matchobj:
                    version = int(matchobj.group(1))

                matchobj = re.search(self.cfile.rmap, line)
                if matchobj:
                    mapstr = matchobj.group(1)                    

        self.assertEqual(version, 88)
        self.assertEqual(mapstr, 'bar')

    def test_get_version_name(self):
        self.assertEqual(self.cfile.get_version_name(18), 'cfile_18.js')
        self.assertEqual(self.cfile.get_version_name(), self.cfile.basename +\
            '_' + str(self.cfile.version) + '.js')

    def test_get_stale_name(self):
        self.cfile.version = 10
        self.assertEqual(self.cfile.get_stale_name(),
            self.cfile.get_version_name(10 - self.cfile.stale_age))

    def test_parse_content(self):
        snippet_1 = 'CN6[\'add\'](\'alice'
        snippet_2 = 'ack\', func'
        snippet_3 = 'dexter'
        snippet_4 = 'priscilla'
        content = ''

        for line in self.cfile.parse_content():
            content += line

        self.assertTrue(content.find(snippet_1) > -1)
        self.assertTrue(content.find(snippet_2) > -1)
        self.assertTrue(content.find(snippet_3) > -1)
        self.assertTrue(content.find(snippet_4) > -1)
        self.assertTrue(content.find('depend(') == -1)

    def test_update_map(self):
        snippet_1 = 'cfile_100.js'
        snippet_2 = "'lucy','alice','jack'"
        snippet_3 = 'jquery.js'

        self.cfile.update_map()
        mapstr = self.cfile.map

        self.assertTrue(mapstr.find(snippet_1) > -1)
        self.assertTrue(mapstr.find(snippet_2) > -1)
        self.assertTrue(mapstr.find(snippet_3) > -1)

    def test_dump(self):
        content = self.cfile.dump(['1', '2'])

        self.assertTrue('2' in content)
        self.assertTrue('});\n' in content)
        self.assertTrue(
            "    CN6.add('jack', function(C) {\n" in content);

    def test_push(self):
        self.cfile.push(test_path)

        self.assertTrue(os.path.exists(test_path + \
            self.cfile.get_version_name()))

    def test_update_referrer(self):
        self.cfile.version = 66
        self.cfile.update_referrer(test_path + 'referrer.txt')

        with open(test_path + 'referrer.txt') as handler:
            content = handler.read()
            self.assertTrue(content.find('cfile_66.js'))

    def test_css(self):
        cfile = CFile(test_path + 'cfile.css')
        content = ''.join(cfile.dump())

        self.assertTrue('red' in content and 'blue' in content and \
            'yellow' in content)

    def test_fill_placeholder(self):
        holder_cfile = CFile(test_path + 'cfile_holder.css')
        referrer_path = test_path + 'referrer.txt'
        holder_cfile.update_referrer(referrer_path)

        with open(referrer_path) as handler:
            self.assertTrue(handler.read().find('.a{') > -1)
        

if __name__ == '__main__':
    unittest.main()
