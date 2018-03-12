# coding=utf-8

import env
import unittest
import os
import shutil
import random
import logging
from bomb.batch import Batch
from bomb.utils import normalize_path
from env import root_path, test_path

logger = logging.getLogger('bomb')

CONFIG_CONTENT = '''{

    "cfile": [""],

    "referrer":["../referrer.txt"],

    "store": "../store/",
    
    "prefix_path": {
        "lib": "../../../lib/"
    }
}
'''

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

C4_CSS = '''/*@version = 1*/
'''

REFERRER_CONTENT = '''
<title>中文</title>
<script src="//domain/path/static/c1_0.js"></script>
<script src="//domain/path/static/c2_0.js"></script>
<script src="//domain/path/static/c3_0.js"></script>
<link ref="stylesheet" type="text/css" href="//domain/path/static/c4_0.css" />
'''

class TestBatch(unittest.TestCase):

    def setUp(self):
        workspace = test_path + 'workspace'
        build = normalize_path(workspace + '/build/')
        store = normalize_path(workspace + '/store/')
        os.mkdir(workspace)
        os.mkdir(build)
        os.mkdir(store)

        for filename, file_content in [('c1.js', C1_JS), ('c2.js', C2_JS),
            ('c3.js', C3_JS), ('c4.css', C4_CSS), 
            ('config.json', CONFIG_CONTENT)]:
            path = normalize_path(build + filename)
            with open(path, 'w') as handler:
                handler.write(file_content)

        with open(workspace + os.sep + 'referrer.txt', 'w') as handler:
            handler.write(REFERRER_CONTENT)

    def tearDown(self):
        shutil.rmtree(test_path + 'workspace')


    def test_batch(self):
        batch = Batch(normalize_path(test_path + 'workspace/build/config.json'))
        batch.list()
        batch.filter([3])
        batch.filter([1])
        batch.publish()

        logger.debug('====================================================')
        group = [item.index for item in batch.group.list(True)]
        for i in range(10):
            selected = random.sample(group, 2)
            print(selected)
            batch.filter(selected)
            batch.publish()
            logger.debug('====================================================')


if __name__ == '__main__':
    unittest.main()
