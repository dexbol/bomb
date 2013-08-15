# coding=utf-8

import env
import os
import unittest
from bomb import compiler

class TestCompiler(unittest.TestCase):
	
	def setUp(self):
		with open(env.test_path + 'aa.js', 'w') as handler:
			handler.write('/* test js */')

		with open(env.test_path + 'aa.css', 'w') as handler:
			handler.write('/* test css */')

	def tearDown(self):
		try:
			os.remove(env.test_path + 'aa.js')
			os.remove(env.test_path + 'aa.css')
			os.remove(env.test_path + 'bb.js')
			os.remove(env.test_path + 'bb.css')
		except:
			pass

	def test_compile_js(self):
		compiler.compile_js(env.test_path + 'aa.js', env.test_path + 'bb.js')
		self.assertTrue(os.path.exists(env.test_path + 'bb.js'))

	def test_compile_css(self):
		compiler.compile_css(env.test_path + 'aa.css', env.test_path + 'bb.css')
		self.assertTrue(os.path.exists(env.test_path + 'bb.css'))


if __name__ == '__main__':
	unittest.main()