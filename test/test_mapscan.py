# coding=utf-8

import env
import bomb.mapscan as bombmap
import unittest
import logging
import os

ONE_JS = '''
DEX.add('namespace.module', function() {
    // some code

}, {requires: ['1', '2']});

CN6.add('namespace.other', function() {
    // some code
}, {requires: ['1', '2', 
'3', 
'4']});

'''

MUSTACHE_JS = '''
;(function() {
    var mustache = {}

})();
'''

class TestMap(unittest.TestCase):

    def setUp(self):
        with open(env.test_path + 'one.js', 'w') as handler:
            handler.write(ONE_JS)

        with open(env.test_path + 'mustache-1.2-min.js', 'w') as handler:
            handler.write(MUSTACHE_JS)

    def tearDown(self):
        try:
            os.remove(env.test_path + 'one.js')
            os.remove(env.test_path + 'mustache-1.2-min.js')
            os.remove(env.test_path + 'testmap.js')
        except:
            pass

    def test_scan_module(self):
        result = bombmap._buildMapFromFile(env.test_path + 'one.js',
            env.root_path)
        self.assertTrue(len(result) == 2)

        first = result[0]
        second = result[1]

        self.assertEqual(first.modulename, 'namespace.module')
        self.assertEqual(second.modulename, 'namespace.other')

        self.assertEqual(first.path, 'test/one.js')

        self.assertEqual(first.modulerequire, "'1', '2'")
        self.assertEqual(second.modulerequire, "'1', '2', \n'3','4'")

        result = bombmap._buildMapFromFile(env.test_path + 'mustache-1.2-min.js',
            env.root_path)
        result = result[0]

        self.assertEqual(result.modulename, 'mustache')


    def test_write_map(self):
        bombmap.write(env.test_path, boom='FOO', dest='testmap.js')
        self.assertTrue(os.path.exists(env.test_path + 'testmap.js'))


if __name__ == '__main__':
    unittest.main()