#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
import subprocess
import toml  # type: ignore
from .session import Session
from .widget import Widget, parse_widget


## Functions
def _entry() -> None:
    # -<SAVE>
    session = Session.current()
    print("--INPUT--")
    print(session, end ="\n--------------------------------------------\n")
    windows = []
    for window in session.windows:
        panes = []
        wind = { 'pos': window.position, 'size': window.size }
        windows.append(wind)
        if not window.children:
            wind['id'] = window.id
            continue
        wind['orientation'] = window.orientation
        # -Handle children
        for child in window.children:
            # -TODO: Handle nested children
            pane = { 'pos': child.position, 'size': child.size }
            pane['id'] = child.id
            panes.append(pane)
        wind['pane'] = panes
    with open(".pymux-session", 'w') as f:
        toml.dump({
            'project': { 'name': session.name },
            'window': windows
        }, f)
    # -<LOAD>
    session = None
    with open(".pymux-session", 'r') as f:
        data = toml.load(f)
    session = Session.new(data['project']['name'])
    for window in data['window']:
        wind = Widget(tuple(window['pos']), tuple(window['size']))
        session.windows.append(wind)
        if 'pane' not in window:
            wind._id = window['id']
            continue
        # -Handle children
        wind.orientation = window['orientation']
        for pane in window['pane']:
            # -TODO: Handle nested children
            child = Widget(tuple(pane['pos']), tuple(pane['size']))
            child._id = pane['id']
            wind.children.append(child)
    print("--OUTPUT--")
    print(session, end ="\n--------------------------------------------\n")


## Body
if __name__ == "__main__":
    _entry()
