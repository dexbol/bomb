# coding=utf-8

import os
import unittest
import shutil
import logging
from env import test_path, root_path
from bomb.cfilegroup import CFileGroup
from bomb.utils import normalize_path

C1_JS = '''/*@bootstrap*/
$depend('jquery');
'''

C2_JS = '''/*@map=c2map*/
$depend('jquery')
'''

C3_JS = '''/*@map=c3map*/
$depend('jquery');
$depend('mustache')
'''

C4_CSS = '''@import url('example.css')
'''

class TestCFileGroup(unittest.TestCase):

    def setUp(self):
        os.mkdir(test_path + 'cfile')
        for filename, file_content in [('c1.js', C1_JS), ('c2.js', C2_JS),
            ('c3.js', C3_JS), ('c4.css', C4_CSS)]:

            path = normalize_path(test_path + 'cfile/' + filename)
            with open(path, 'w') as handler:
                handler.write(file_content)

        group = CFileGroup()
        group.add_by_path(test_path + 'cfile' + os.sep)
        self.group = group

    def tearDown(self):
        try:
            shutil.rmtree(test_path + 'cfile')
        except IOError:
            pass

    def test_filter(self):
        self.group.filter([0,1])
        for item in self.group.list():
            self.assertTrue(item.index in [0, 1])

        idx = self.group.pick('c3.js').index
        self.group.filter([idx])
        self.assertTrue(not self.group.pick('c3.js').frozen)
        self.assertTrue(not self.group.pick('c1.js').frozen)

        idx = self.group.pick('c4.css').index
        self.group.filter([idx])
        self.assertTrue(self.group.pick('c1.js').frozen)
        self.assertTrue(not self.group.pick('c4.css').frozen)

    def test_pick(self):
        self.assertEqual(self.group.pick('c1.js').filename, 'c1.js')
        self.assertEqual(self.group.pick('dexter'), None)

    def test_list(self):
        group = self.group

        group.pick('c2.js').frozen = True
        for item in group.list():
            self.assertTrue(item.filename != 'c2.js')

        counter = 0
        for item in group.list(True):
            counter += 1
        self.assertEqual(counter, 4)

    def test_dump(self):
        group = self.group

        self.assertTrue('/*@map=c2map*/\n' in group.dump('c2.js'))
        self.assertTrue('c2map' in group.dump('c1.js') and
            'c3map' in group.dump('c1.js'))


if __name__ == '__main__':
    unittest.main()
