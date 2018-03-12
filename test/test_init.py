# coding=utf-8

from env import test_path
import os
import unittest
from bomb.init import init_config

class TestInitConfig(unittest.TestCase):

    def setUp(self):
        init_config(test_path)

    def tearDown(self):
        os.remove(test_path + 'config.json')

    def test_init(self):
        self.assertTrue(os.path.exists(test_path + 'config.json'))


if __name__ == '__main__':
    unittest.main()
