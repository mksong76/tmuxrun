#!/usr/bin/env python3

from setuptools import setup

setup(
    name="tmuxrun",
    version="0.1.0",
    py_modules=['tmux'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'tmx = tmux.main:main',
        ]
    }
)
