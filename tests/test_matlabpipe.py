# -*- coding: utf-8 -*-
#
# test_matlabpipe.py
#

"""This test needs an installed copy of MatlabTM."""

import nose
import unittest
from matlabpipe import MatlabPipe, MatlabError


class TestMatlabPipe(unittest.TestCase):
    def setUp(self):
        try:
            self.matlab = MatlabPipe(matlab_process_path=None,
                                     matlab_version=None)
            self.matlab.open()
        except IOError:
            raise nose.SkipTest

    def tearDown(self):
        self.matlab.close()

    def test_eval(self):
        for i in xrange(100):
            ret = self.matlab.eval('disp \'hiush world%s\';' % ('b'*i))
            self.assertTrue('hiush world' in ret)

    def test_put(self):
        self.matlab.put({'A': [1, 2, 3]})
        ret = self.matlab.eval('A')
        self.assertTrue('A =' in ret)

    def test_1_element(self):
        self.matlab.put({'X': 'string'})
        ret = self.matlab.get('X')
        self.assertEquals(ret, 'string')

    def test_get(self):
        self.matlab.eval('A = [1 2 3];')
        ret = self.matlab.get('A')
        self.assertEquals(ret[0], 1)
        self.assertEquals(ret[1], 2)
        self.assertEquals(ret[2], 3)

    def test_error_undef(self):
        self.assertRaises(MatlabError, self.matlab.eval, 'no_such_function')

    def test_error(self):
        self.assertRaises(MatlabError, self.matlab.eval, 'sin')

if __name__ == '__main__':
    unittest.main()
