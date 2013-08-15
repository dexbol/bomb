# coding=utf-8

import env
import logging
import re
import os
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
'''

MODULE_1_CONTENT = '''
CN6.add('lucy',   function() {
	// code
});

CN6.add('alice', function(C) {
	//code
})
'''

MODULE_2_CONTENT = '''
	CN6.add('jack', function(C) {

		// code
		});
'''

REFERRER_CONTENT = '''
<title>中文</title>
<script src="//domain/path/static/cfile_0.js"></script>

'''

class TestCFile(unittest.TestCase):

	def setUp(self):
		with open(test_path + 'module_1.js', 'w') as handler:
			handler.write(MODULE_1_CONTENT)

		with open(root_path + 'module_2.js', 'w') as handler:
			handler.write(MODULE_2_CONTENT)

		with open(test_path + 'cfile.js', 'w') as handler:
			handler.write(CFILE_CONTENT)

		with open(test_path + 'referrer.txt', 'w') as handler:
			handler.write(REFERRER_CONTENT)

		self.cfile = CFile(test_path + 'cfile.js', url_map={
			'root': normalize_path('../')
			})

	def tearDown(self):
		try:
			os.remove(test_path + 'module_1.js')
			os.remove(root_path + 'module_2.js')
			os.remove(test_path + 'cfile.js')
			os.remove(test_path + 'referrer.txt')
			os.remove(test_path + self.cfile.get_version_name())
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
		snippet_1 = 'CN6.add(\'alic'
		snippet_2 = 'ack\', func'
		content = ''

		for line in self.cfile.parse_content():
			content += line

		self.assertTrue(content.find(snippet_1) > -1)
		self.assertTrue(content.find(snippet_2) > -1)

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
		self.assertTrue("CN6.add('alice', function(C) {\n" in content);

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


if __name__ == '__main__':
	unittest.main()

