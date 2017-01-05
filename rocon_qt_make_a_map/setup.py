#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rocon_qt_make_a_map'],
    package_dir={'': 'src'},
    scripts=['scripts/rocon_make_a_map'],
)
setup(**d)
