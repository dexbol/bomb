# coding=utf-8

import env
from bomb import utils
from os import path
import unittest

class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normalize_path(self):
        self.assertEqual(utils.normalize_path('foo/bar/../test/'), 
            'foo/test/')
        self.assertEqual(utils.normalize_path('C:\\windows\\User\\Desktop\\'), 
            'C:\\windows\\User\\Desktop\\')
        self.assertEqual(utils.normalize_path('../test/foo.js'), 
            '../test/foo.js')
        self.assertEqual(utils.normalize_path('bar.js'), 'bar.js')

    def test_filename(self):
        result = utils.filename('xx/foo/bar.123.js')
        filename, basename, extension = result

        self.assertEqual(filename, 'bar.123.js')
        self.assertEqual(extension, 'js')
        self.assertEqual(basename, 'bar.123')


if __name__ == '__main__':
    unittest.main()