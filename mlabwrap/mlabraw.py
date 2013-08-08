#!/usr/bin/env python


from matlabpipe import MatlabPipe as MatlabConnection


def open(arg):
    matlab_path = 'guess'
    try:
        ret = MatlabConnection(matlab_path)
        ret.open()
    except:
        print('Could not open MatlabTM, is it in %s?') % matlab_path
    return ret


def close(matlab):
    matlab.close()


def eval(matlab, exp):
    matlab.eval(exp, print_expression=False, on_new_output=None)
    return ''


def get(matlab, var_name):
    return matlab.get(var_name)


def put(matlab, var_name, val):
    matlab.put({var_name: val})
