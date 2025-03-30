#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
import subprocess
import toml
from .parser import parse_layout


## Functions
def calculate_checksum(source: str) -> int:
    checksum: int = 0
    for c in source:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += ord(c)
    return checksum


def _entry() -> None:
    # -<SAVE>
    # list-windows + layout
    result = subprocess.run(['tmux', 'list-windows', '-F', '"#{window_layout}"'], capture_output=True, text=True)
    for i, window in enumerate(result.stdout.split('\n')):
        # -Ignore empty
        if window == '':
            continue
        # -Remove quotes
        window = window[1:-1]
        # -Validate checksum
        checksum = int(window[:4], 16)
        window = window[5:]
        assert checksum == calculate_checksum(window)
        # -Layout
        print(f"Input[{i}] '{window}'")
        wind = parse_layout(window)
        print(wind)
        # -Window


## Body
if __name__ == "__main__":
    _entry()
