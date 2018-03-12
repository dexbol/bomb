# coding=utf-8

from env import test_path
from bomb.config import Config
import os
import unittest

CONFIG_FILE_CONTENT = '''

// =====  config file example  ====
// rename config.json and copy to your build path
// all directory path are relative to current path (build path)
{
    // path that need parse
    "cfile_path": "config/",

    //sepement by comma
    "template":["../../../../../template/profile/header.tpl"],

    "store": "../../../_/",
    
    "prefix_path": {
        "lib": "../../../lib/"
    }
}

'''

class TestConfig(unittest.TestCase):

    def setUp(self):
        with open(test_path + 'config.json', 'w') as handler:
            handler.write(CONFIG_FILE_CONTENT)

        self.config = Config()
        self.config.load(test_path + 'config.json')

    def tearDown(self):
        try:
            os.remove(test_path + 'config.json')
        except:
            pass

    def test_get(self):
        prefix = self.config.get('prefix_path')
        self.assertEqual(prefix['lib'], '../../../lib/')

    def test_set(self):
        self.config.set('name', 'dexbol')
        self.assertEqual(self.config.get('name'), 'dexbol')


if __name__ == '__main__':
    unittest.main()
