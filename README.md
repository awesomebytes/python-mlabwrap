python-mlabwrap
===============

[![Build](https://badge.fury.io/py/ctd.png)](http://badge.fury.io/py/ctd)
[![Build](https://api.travis-ci.org/ocefpaf/python-ctd.png?branch=master)](https://travis-ci.org/ocefpaf/python-ctd)
[![Downloads](https://pypip.in/d/ctd/badge.png)](https://crate.io/packages/ctd/)


A [Freecell's mlabwrap](http://code.google.com/p/danapeerlab/source/browse/trunk/freecell/depends/common/python/matlabpipe.py)
fork for raw communication with Matlab(TM) using pipes under unix.

This version differs slightly from the original in the path and version
detection.  The original was optimized for Mac's here we use unix `which`
command for the directory and the actual directory name for the version.

The code is also `pep8` and `python3` (untested) compliant.  We also added some
modification to make it compatible with MatlabTM R2013a.

The original version also provide `mlabraw.py` and `mlabwrap.py` for seamless
use in an interactive session.  This fork however is aimed to provide a way to
write "wrappers" around some functions that are not yet present in python in a
more `explicit` way:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ {.python .numberLines}
from matlabpipe import MatlabPipe
matlab = MatlabPipe(matlab_version='2013a')
matlab.open()
def t_tide(arr, fout=None):
    lat = 42.7
    interval = dt
    start = ', '.join([str(k) for k in dates[0].timetuple()[:6]])

    matlab.put({'arr': detrend(arr)})
    cmd = r"""[tidestruc, pout] = t_tide(arr, ...
            'interval', %s, ...
               'start', datenum(%s), ...
            'latitude', %s, ...
               'error', 'cboot', ...
           'synthesis', 1, ...
              'output', '%s');""" % (interval, start, lat, fout)
    out = matlab.eval(cmd)
    map(matlab.eval, ("freq = tidestruc.freq;",
                      "tidecon = tidestruc.tidecon;",
                      "name = tidestruc.name;"))
    pout, freq, tidecon, name = map(matlab.get,
                                    ('pout', 'freq', 'tidecon', 'name'))
    return pout, freq, tidecon, name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
