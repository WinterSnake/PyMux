#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Session                       ##
##-------------------------------##

## Imports
from __future__ import annotations
import subprocess
from .widget import Widget


## Classes
class Session:
    """
    Tmux Session
    Represents a tmux session with details to restore/save/load
    """

    # -Constructor
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.windows: list[Widget] = []

    # -Dunder Methods
    def __str__(self) -> str:
        session: str = self.name + ":\n"
        for i, window in enumerate(self.windows):
            session += ' ' + str(window)
            if i < len(self.windows) - 1:
                session += '\n'
        return session

    # -Instance Methods
    def attach(self) -> None:
        '''Attach session to client'''
        subprocess.run(['tmux', 'attach-session', '-t', self.name])

    def close(self) -> None:
        '''Close and kill session'''
        subprocess.run(['tmux', 'kill-session', '-t', self.name])

    # -Static Methods
    @staticmethod
    def current() -> Session | None:
        '''Gets currently open session'''
        name = subprocess.run(
            ['tmux', 'display-message', '-p', '#{session_name}'],
            capture_output=True, text=True
        )
        session = Session(name.stdout[:-1])
        layouts = subprocess.run(
            ['tmux', 'list-windows', '-F', '#{window_layout}'],
            capture_output=True, text=True
        )
        # -Windows
        for i, layout in enumerate(layouts.stdout.split('\n')):
            # -Ignore Empty
            if layout == '':
                continue
            window = Widget.from_layout(layout)
            session.windows.append(window)
            # -TODO: Processes
        return session

    @staticmethod
    def get_if_exists(name: str) -> Session | None:
        '''Returns tmux session if it exists'''
        result = subprocess.run(
            ['tmux', 'has-session', '-t', name],
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            return None
        session = Session(name)
        return session

    # -Class Methods
    @classmethod
    def new(cls, name: str) -> Session:
        '''Create a new tmux session and return object'''
        subprocess.run(['tmux', 'new-session', '-d', '-s', name])
        return Session(name)
