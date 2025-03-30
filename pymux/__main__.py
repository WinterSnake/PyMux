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
def usage(message: str | None) -> None:
    """
    """
    print(f"\x1b[1;31m{message}\x1b[0m")
    sys.exit(1)


def _entry() -> None:
    cli = sys.argv.pop(0)
    if len(sys.argv) < 1:
        usage("No valid mode provided")
    mode: str = sys.argv.pop(0)
    # -<SAVE>
    if mode == 'save':
        session = Session.current()
        windows = []
        for window in session.windows:
            wind = { 'pos': window.position, 'size': window.size }
            windows.append(wind)
            if not window.children:
                continue
            # -Handle children
            panes = []
            pane_stack: list[dict] = []
            widget_stack: list[Widget] = window.children
            wind['orientation'] = window.orientation
            while widget_stack:
                widget = widget_stack.pop()
                if widget is None:
                    pane_stack.pop()
                    continue
                pane = { 'pos': widget.position, 'size': widget.size }
                if pane_stack:
                    pane['parent'] = pane_stack[-1]
                if not widget.children:
                    panes.append(pane)
                    continue
                pane['orientation'] = widget.orientation
                pane_stack.append(None)
                pane_stack.append(pane)
                widget_stack.extend(widget.children)
            wind['pane'] = panes
        with open(".pymux-session", 'w') as f:
            toml.dump({
                'project': { 'name': session.name },
                'window': windows
            }, f)
    # -<LOAD>
    elif mode == 'load':
        with open(".pymux-session", 'r') as f:
            data = toml.load(f)
        # -Reattach Session
        session: Session | None
        if session := Session.get_if_exists(data['project']['name']):
            session.attach()
            return
        # -Create Session
        session = Session.new(data['project']['name'])
        for window in data['window']:
            wind = Widget(tuple(window['pos']), tuple(window['size']))
            session.windows.append(wind)
            if 'pane' not in window:
                continue
            # -Handle children
            wind.orientation = window['orientation']
            for pane in window['pane']:
                widget = Widget(tuple(pane['pos']), tuple(pane['size']))
                if 'parent' not in pane:
                    wind.children.append(widget)
                    continue
                # -Handle parent widgets
                parent = pane.pop('parent')
                parent_widget = wind.get_or_create_child(
                    tuple(parent['pos']), tuple(parent['size']), parent['orientation']
                )
                parent_widget.children.append(widget)
        session.attach()


## Body
if __name__ == "__main__":
    _entry()
