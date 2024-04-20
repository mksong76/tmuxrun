#!/usr/bin/env python3

from typing import List, Tuple
import os
import math

class TMux:
    def __init__(self, cmd, rows=None, cols=None):
        self.pans: List['Pan'] = []
        self.cmds = [cmd, "-2", "new-session"]
        self.rows = rows
        self.cols = cols
        self.sync = False
        self.mouse = True
    def new_pan(self, row=None, col=None) -> 'Pan':
        p = Pan(row=row, col=col)
        self.pans.append(p)
        return p

    def get_size(self) -> Tuple[int, int]:
        pans = max(len(self.pans),1)
        if self.rows is None:
            cols = self.cols
            if cols is None:
                cols = math.ceil(math.sqrt(pans))
            rows = (pans+cols-1) // cols
            return rows, cols
        else:
            cols = (pans+self.rows-1) // self.rows
            return self.rows, cols

    def add_cmd(self, cmd):
        self.cmds.append(";")
        if type(cmd) is list:
            self.cmds += cmd
        else:
            self.cmds += str(cmd).split(" ")

    def map_panes(self):
        rows, cols = self.get_size()

        pans = []
        for row in range(rows):
            pans.append([None]*cols)

        for w in self.pans:
            for idx in range(rows*cols):
                row = idx // cols
                col = idx % cols
                if pans[row][col] is not None:
                    continue
                if (w.row is None or w.row == row) and \
                    (w.col is None or w.col == col):
                    pans[row][col] = w
                    break
        return pans, rows, cols

    def load_pan_configs(self, configs):
        for config in configs:
            pan = self.new_pan()
            pan.load(config)

    def load(self, config):
        if type(config) is dict:
            for k, v in config.items():
                if k == 'rows':
                    self.rows = int(v)
                elif k == 'cols':
                    self.cols = int(v)
                elif k == 'pans':
                    self.load_pan_configs(v)
                elif k == 'sync':
                    self.sync = bool(v)
                elif k == 'mouse':
                    self.mouse = bool(v)
                else:
                    raise Exception(f"Unknonwn option={k}")
        elif type(config) is list:
            self.load_pan_configs(config)
        else:
            self.load_pan_configs([str(config)])

    @staticmethod
    def percent_of(idx, total):
        remain = total - idx
        return remain * 100 // (remain+1)

    def execute(self):
        if self.mouse:
            self.add_cmd(["set-option", "-g", "mouse", "on"])
        pans, rows, cols = self.map_panes()
        cwd = os.getcwd()
        for row in range(1, rows):
            self.add_cmd([
                "split-window", "-v",
                "-l", f"{TMux.percent_of(row, rows)}%",
                "-c", cwd ])

        for row in range(rows):
            for col in range(1, cols):
                self.add_cmd(["select-pane", "-t", f"{row*cols+col-1}"])
                self.add_cmd([
                    "split-window", "-h",
                    "-l", f"{TMux.percent_of(col, cols)}%",
                    "-c", cwd ])

        for row in range(rows):
            for col in range(cols):
                item = pans[row][col]
                if item is None:
                    continue
                self.add_cmd([
                    "select-pane", "-t", f"{row*cols+col}"
                ])
                item.execute(self)
        if self.sync:
            self.add_cmd(["set-option", "-w", "synchronize-panes", "on"])
        return os.execvp(self.cmds[0], self.cmds)

class Pan:
    def __init__(self, row=None, col=None):
        self.row = row
        self.col = col
        self.cmds = []

    def add_cmd(self, cmd):
        if type(cmd) is list:
            self.cmds.append(cmd)
        else:
            self.cmds.append(["send-keys", cmd, "C-m"])

    def load(self, config):
        if type(config) is object:
            for k, v in config.items():
                if k == 'row':
                    self.row = int(v)
                elif k == 'col':
                    self.col = int(v)
                elif k == 'cmds':
                    for cmd in v:
                        self.add_cmd(cmd)
                elif k == 'cmd':
                    self.add_cmd(v)
        elif type(config) is list:
            for cmd in config:
                self.add_cmd(cmd)
        elif type(config) is str:
            self.add_cmd(config)

    def add_keys(self, *args):
        self.cmds.append(["send-keys", *args])

    def execute(self, tmux):
        for cmd in self.cmds:
            tmux.add_cmd(cmd)


def start(config, tmux="tmux"):
    s = TMux(tmux)
    s.load(config)
    s.execute()
