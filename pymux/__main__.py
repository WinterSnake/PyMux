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
    # list-windows + layout
    session = Session()
    result = subprocess.run(['tmux', 'list-windows', '-F', '"#{window_layout}"'], capture_output=True, text=True)
    for i, layout in enumerate(result.stdout.split('\n')):
        # -Ignore empty
        if layout == '':
            continue
        # -Remove quotes
        layout = layout[1:-1]
        window = Widget.from_layout(layout)
        print(window.layout)


## Body
if __name__ == "__main__":
    _entry()
