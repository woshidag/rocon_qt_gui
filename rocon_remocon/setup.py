#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rocon_remocon'],
    package_dir={'': 'src'},
    scripts=['scripts/rqt_remocon', 'scripts/wrqt_remocon' ],
)
setup(**d)
