##-------------------------------##
## PyMux Session                 ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Session                       ##
##-------------------------------##

## Imports
from __future__ import annotations
import os
import subprocess
from collections.abc import Iterable
from .widget import Widget


## Functions
def _run_command(*command: str) -> str:
    command = ("tmux", *command)
    process = subprocess.run(command, capture_output=True, text=True)
    return process.stdout.strip()


def _parse_window_widget(session: str, source: str) -> Widget:
    """Returns a parsed window widget with child panes and processes"""
    name, index, layout = source.split(';')
    widget = Widget.from_layout(layout)
    widget.name = name
    pane_data = _run_command(
            "list-panes", "-t", f"{session}:{index}", "-F",
        "#{pane_index};#{pane_id};#{pane_pid}"
    )
    for _pane, (i, pane) in zip(pane_data.split('\n'), enumerate(widget)):
        idx, _id, pid = _pane.split(';')
        assert i == int(idx) and pane.id == int(_id[1:])
    return widget


## Classes
class Session:
    """
    Tmux Session
    Represents a tmux session with name, windows, and panes
    Includes methods to interact with session programatically
    """

    # -Constructor
    def __init__(self, name: str, windows: Iterable[Widget]) -> None:
        self.name: str = name
        self.windows: Iterable[Widget] = windows

    # -Static Methods
    @staticmethod
    def current() -> Session | None:
        if not "TMUX" in os.environ:
            return None
        name = _run_command("display", "-p", "#{session_name}")
        windows: list[Widget] = []
        window_data = _run_command(
            "list-windows", "-F",
            "#{window_name};#{window_index};#{window_layout}"
        )
        for window in window_data.split('\n'):
            widget = _parse_window_widget(name, window)
            windows.append(widget)
        return Session(name, windows)
