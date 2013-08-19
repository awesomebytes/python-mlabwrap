# -*- coding: utf-8 -*-
#
# test_t_tide.py
#
# purpose:  Test MatlabPipe with t_tide toolbox.
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.tiddlyspot.com/
# created:  26-Sep-2011
# modified: Fri 09 Aug 2013 03:39:30 PM BRT
#
# obs:
#

from mlabwrap import MatlabPipe


def t_demo():
    """Call Matlab and run t_tide demos."""
    path, version = '/home/filipe/00-NOBKP/R2013a/bin/matlab', '2013a'
    matlab = MatlabPipe(matlab_process_path=path, matlab_version=version)
    matlab.open()
    cmd = """load t_example
    infername = ['P1';'K2'];
    inferfrom = ['K1';'S2'];
    infamp    = [0.33093; 0.27215];
    infphase  = [-7.07; -22.40];

    [tidestruc, pout] = t_tide(tuk_elev,...
    'interval', 1, ...                   % Hourly data.
    'start', tuk_time(1),...             % Start time is datestr(tuk_time(1)).
    'latitude', 69 + 27 / 60,...         % Latitude of observations.
    'inference', infername, inferfrom, infamp, infphase,...
    'shallow', 'M10',...                 % Add a shallow-water constituent.
    'error', 'linear',...                % coloured bootstrap CI.
    'synthesis', 1);                     % Use SNR = 1 for synthesis.
    """
    out = matlab.eval(cmd)
    del(out)
    matlab.close()
    return None

if __name__ == '__main__':
    t_demo()
