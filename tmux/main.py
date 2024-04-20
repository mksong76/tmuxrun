#!/usr/bin/env python3

import os
import click

from . import tmux
import json

@click.command()
@click.argument('config')
@click.option('--tmux', 'tmux_cmd', type=click.STRING, envvar="TMUX", default='tmux')
def main(config: str, tmux_cmd: str):
    if os.path.exists(config):
        with open(config, 'rt') as fd:
            config = json.load(fd)
    tmux.start(config, tmux_cmd)
