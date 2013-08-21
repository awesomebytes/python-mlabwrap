# -*- coding: utf-8 -*-

import os
import sys
import fcntl
import select
import subprocess
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import numpy as np
from scipy.io import savemat, loadmat

__all__ = ['MatlabError',
           'MatlabConnectionError',
           'MatlabPipe']


class MatlabError(Exception):
    """Raised for errors inside MatlabTM."""
    pass


class MatlabConnectionError(Exception):
    """Raised for errors related to the MatlabTM connection."""
    pass


def find_matlab_process():
    """"Try to get MatlabTM directory using system `which` command."""
    p = subprocess.Popen(['which', 'matlab'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        path = list(p.stdout.readlines())[0].strip()
    except IndexError:
        return None
    if 'no matlab in' in path.decode('utf-8'):
        return None
    else:
        return os.path.realpath(path)


def find_matlab_version(process_path):
    """Tries to get MatlabTM version according to its process path."""
    bin_path = os.path.dirname(process_path)
    matlab_path = os.path.dirname(bin_path)
    matlab_dir_name = os.path.basename(matlab_path)
    version = matlab_dir_name.decode('utf-8').replace('R', '')  # Linux.
    version = version.replace('MATLAB_', '').replace('.app', '')
    if not is_valid_version_code(version):
        return None
    return version


def is_valid_version_code(ver):
    """Checks that the given version code is valid."""
    letters = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    numbers = list(range(1990, 2050))
    if ver is not None and len(ver) == 5 and int(ver[:4]) in numbers and \
       ver[4] in letters:
        return True
    else:
        False


class MatlabPipe(object):
    """Manages a connection to a MatlabTM process.  MatlabTM version is in the
    format [YEAR][VERSION] for example: 2013b.  The process can be opened and
    close with the open/close methods.  To send a command to the MatlabTM
    shell use 'eval'.  To load NumPy data to the MatlabTM shell use 'put'.
    To retrieve NumPy data from the MatlabTM shell use 'get'."""

    def __init__(self, matlab_process_path=None, matlab_version=None):
        """MatlabTM path should be a path to the MatlabTM executable."""
        if not matlab_process_path:
            matlab_process_path = find_matlab_process()
            if matlab_process_path is None:
                raise IOError("Cannot find a valid matlab path")
        if not os.path.exists(matlab_process_path):
            raise ValueError('Matlab process path %s does not exist' %
                             matlab_process_path)
        if not matlab_version:
            matlab_version = find_matlab_version(matlab_process_path)
        if not is_valid_version_code(matlab_version):
            raise ValueError('Invalid version code %s' % matlab_version)

        self.matlab_version = (int(matlab_version[:4]), matlab_version[4])
        self.matlab_process_path = matlab_process_path
        self.process = None
        self.command_end_string = '___MATLAB_PIPE_COMMAND_ENDED___'
        self.expected_output_end = '%s\n>> ' % self.command_end_string
        self.stdout_to_read = ''

    def open(self, print_matlab_welcome=True):
        """Opens the MatlabTM process."""
        if self.process and not self.process.returncode:
            raise MatlabConnectionError('Matlab(TM) process is still'
                                        'active. Use close to close it')
        self.process = subprocess.Popen([self.matlab_process_path, '-nojvm',
                                         '-nodesktop'], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        flags = fcntl.fcntl(self.process.stdout, fcntl.F_GETFL)
        fcntl.fcntl(self.process.stdout, fcntl.F_SETFL, flags |
                    os.O_NONBLOCK)

        if print_matlab_welcome:
            self._sync_output()
        else:
            self._sync_output(None)

    def close(self):
        """Closes the MatlabTM process."""
        self._check_open()
        self.process.stdin.close()

    def eval(self, expression, identify_errors=True, print_expression=False,
             on_new_output=sys.stdout.write):
        """Evaluates a MatlabTM expression synchronously.  If
        identify_erros is true, and the last output line after evaluating
        the expressions begins with '???' and exception is thrown with the
        MatlabTM error following the '???'.  If on_new_output is not None,
        it will be called whenever a new output is encountered.  The
        default value prints the new output to the screen.  The return
        value of the function is the MatlabTM output following the call."""

        self._check_open()
        if print_expression:
            print(expression)
        self.process.stdin.write(expression)
        self.process.stdin.write('\n')
        ret = self._sync_output(on_new_output)
        if identify_errors:
            search = ['Undefined', 'Error', '???']
            for s in search:
                if ret.rfind(s) != -1:
                    raise MatlabError(ret)
        return ret

    def put(self, name_to_val, oned_as='row', on_new_output=None):
        """Loads a dictionary of variable names into the Matlab shell.
        oned_as is the same as in scipy.io.matlab.savemat function:
        oned_as : {'column', 'row'}, optional.  If 'column', write 1-D NumPy
        arrays as column vectors.  If 'row', write 1D NumPy arrays as row
        vectors."""
        self._check_open()
        temp = StringIO()
        savemat(temp, name_to_val, oned_as=oned_as)
        temp.seek(0)
        temp_str = temp.read()
        temp.close()
        self.process.stdin.write('load stdio;\n')
        self._read_until('ack load stdio\n', on_new_output=on_new_output)
        self.process.stdin.write(temp_str)
        self._read_until('ack load finished\n', on_new_output=on_new_output)
        self._sync_output(on_new_output=on_new_output)

    def get(self, names_to_get, extract_numpy_scalars=True,
            on_new_output=None):
        """Loads the requested variables from the MatlabTM shell.
        names_to_get can be either a variable name, a list of variable names,
        or None.  If it is a variable name, the values is returned.  If it is
        a list, a dictionary of variable_name -> value is returned.  If it is
        None, a dictionary with all variables is returned.  If
        extract_numpy_scalars is true, the method will convert NumPy scalars
        (0-dimension arrays) to a regular python variable."""
        self._check_open()
        single_itme = isinstance(names_to_get, (unicode, str))
        if single_itme:
            names_to_get = [names_to_get]
        if names_to_get is None:
            self.process.stdin.write('save stdio;\n')
        else:
            for name in names_to_get:
                self.eval('%s;' % name, print_expression=False,
                          on_new_output=on_new_output)
            self.process.stdin.write("save('stdio', '%s', '-v6');\n" %
                                     '\', \''.join(names_to_get))
        self._read_until('start_binary\n', on_new_output=on_new_output)
        temp_str = self._sync_output(on_new_output=on_new_output)
        # MATLAB 2010a adds an extra >> so we need to remove more spaces.
        if self.matlab_version == (2010, 'a'):
            temp_str = temp_str[:-len(self.expected_output_end)-6]
        else:
            temp_str = temp_str[:-len(self.expected_output_end)-3]
        temp = StringIO(temp_str)
        ret = loadmat(temp, chars_as_strings=True, squeeze_me=True)
        temp.close()
        for key in list(ret.keys()):
            # Strings are passed without any modification.
            if isinstance(ret[key], unicode) or isinstance(ret[key], str):
                continue
            # FIXME: Try a smarter way to do this:
            while ret[key].shape and ret[key].shape[-1] == 1:
                ret[key] = ret[key][0]
            if extract_numpy_scalars:
                if isinstance(ret[key], np.ndarray) and not ret[key].shape:
                    ret[key] = ret[key].tolist()
        if single_itme:
            return list(ret.values())[0]
        return ret

    def _check_open(self):
        if not self.process or self.process.returncode:
            raise MatlabConnectionError('Matlab(TM) process is not active.')

    def _read_until(self, wait_for_str, on_new_output=sys.stdout.write):
        all_output = StringIO()
        output_tail = self.stdout_to_read
        while not wait_for_str in output_tail:
            tail_to_remove = output_tail[:-len(output_tail)]
            output_tail = output_tail[-len(output_tail):]
            if on_new_output:
                on_new_output(tail_to_remove)
            all_output.write(tail_to_remove)
            if not select.select([self.process.stdout], [], [], 10)[0]:
                raise MatlabConnectionError('timeout')
            new_output = self.process.stdout.read(65536)
            output_tail += new_output
        chunk_to_take, chunk_to_keep = \
            output_tail.split(wait_for_str, 1)
        chunk_to_take += wait_for_str
        self.stdout_to_read = chunk_to_keep
        if on_new_output:
            on_new_output(chunk_to_take)
        all_output.write(chunk_to_take)
        all_output.seek(0)
        return all_output.read()

    def _sync_output(self, on_new_output=sys.stdout.write):
        string = 'disp(\'%s\');\n' % self.command_end_string
        self.process.stdin.write(string)
        return self._read_until(self.expected_output_end, on_new_output)
