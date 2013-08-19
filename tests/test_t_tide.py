# -*- coding: utf-8 -*-
#
# test_t_tide.py
#
# purpose:  Test MatlabPipe with t_tide toolbox.
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.tiddlyspot.com/
# created:  26-Sep-2011
# modified: Mon 19 Aug 2013 05:33:54 PM BRT
#
# obs:  Example passing data from python to MatlabTM and back to python.
#

import nose
import unittest
from mlabwrap import MatlabPipe


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

    def test_t_tide_demo(self):
        """Call Matlab and run t_tide demos."""
        cmd = """load t_example
        infername = ['P1';'K2'];
        inferfrom = ['K1';'S2'];
        infamp    = [0.33093; 0.27215];
        infphase  = [-7.07; -22.40];

        [tidestruc, pout] = t_tide(tuk_elev, ...
        'interval', 1, ...  % Hourly data.
        'start', tuk_time(1), ...  % Start time is datestr(tuk_time(1)).
        'latitude', 69 + 27 / 60, ...  % Latitude of observations.
        'inference', infername, inferfrom, infamp, infphase, ...
        'shallow', 'M10', ...  % Add a shallow-water constituent.
        'error', 'linear', ...  % coloured bootstrap CI.
        'synthesis', 1);  % Use SNR = 1 for synthesis.
        """
        out = self.matlab.eval(cmd)
        del(out)

if __name__ == '__main__':
    unittest.main()
