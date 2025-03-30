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

    # -Static Methods
    @staticmethod
    def current() -> Session | None:
        '''
        '''
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
