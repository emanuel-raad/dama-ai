#!/usr/bin/env python

from distutils.core import setup

setup(name='Dama',
      version='2.0',
      description='Python Dama Game',
      author='Emanuel Raad',
      author_email='raademang@gmail.com',
      packages=['dama', 'dama.game', 'dama.agents', 'dama.render'],
     )