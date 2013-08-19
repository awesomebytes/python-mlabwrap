#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from mlabwrap import __version__

source = 'http://pypi.python.org/packages/source'
install_requires = ['numpy', 'scipy']

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Education
Topic :: Software Development :: Libraries :: Python Modules
"""

README = open('README.md').read()
CHANGES = open('CHANGES.txt').read()
LICENSE = open('LICENSE.txt').read()

config = dict(name='mlabwrap',
              version=__version__,
              packages=['mlabwrap'],
              test_suite='tests',
              use_2to3=True,
              license=LICENSE,
              long_description='%s\n\n%s' % (README, CHANGES),
              classifiers=filter(None, classifiers.split("\n")),
              description="A fork of Freecell's mlabwrap",
              author='Filipe Fernandes',
              author_email='ocefpaf@gmail.com',
              maintainer='Filipe Fernandes',
              maintainer_email='ocefpaf@gmail.com',
              url='http://pypi.python.org/pypi/mlabwrap/',
              download_url='%s/m/mlabwrap/mlabwrap-%s.tar.gz' % (source,
                                                                 __version__),
              platforms='any',
              keywords=['MatlabTM'],
              install_requires=install_requires)

setup(**config)
