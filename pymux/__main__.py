#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import sys
import subprocess

## Constants


## Functions
def usage(path: str, error: str) -> None:
    """
    """
    print(f"\x1b[1;31m{error}\x1b[0m")
    print(f"Usage: {path} MODE")
    sys.exit(1)


def calculate_checksum(_format: str) -> int:
    """
    """

    checksum: int = 0
    for c in _format:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += ord(c)
    return checksum


def parse_pane(value: str) -> dict[str, tuple[int,int] | int]:
    """
    """
    pane: dict[str, tuple[int, int] | int] = {}
    offset: int = 0
    # -Width
    width: int = 0
    #print(f"Getting width: '{value[offset:]}'", end='')
    while (c := value[offset]).isdigit():
        width = width * 10 + int(c)
        offset += 1
    #print(f"\t||Width={width}")
    offset += 1
    # -Height
    height: int = 0
    #print(f"Getting height: '{value[offset:]}'", end='')
    while (c := value[offset]).isdigit():
        height = height * 10 + int(c)
        offset += 1
    #print(f"\t||Height={height}")
    offset += 1
    pane['size'] = (width, height)
    # -X
    x: int = 0
    #print(f"Getting x: '{value[offset:]}'", end='')
    while (c := value[offset]).isdigit():
        x = x * 10 + int(c)
        offset += 1
    #print(f"\t||X={x}")
    offset += 1
    # -Y
    y: int = 0
    #print(f"Getting y: '{value[offset:]}'", end='')
    while (c := value[offset]).isdigit():
        y = y * 10 + int(c)
        offset += 1
    #print(f"\t||Y={y}")
    pane['pos'] = (x, y)
    if value[offset] == '{':
        return (offset, pane)
    offset += 1
    # -Pane ID
    _id: int = 0
    #print(f"Getting id: '{value[offset:]}'", end='')
    while (c := value[offset]).isdigit():
        _id = _id * 10 + int(c)
        offset += 1
    #print(f"\t||ID={_id}")
    pane['id'] = _id
    if value[offset] == '}':
        return (offset, pane)
    return (offset + 1, pane)


def _entry() -> None:
    cmd: str = sys.argv.pop(0)
    if len(sys.argv) == 0:
        usage(cmd, "Expected MODE parameter")
    mode: str = sys.argv.pop(0)
    if mode not in ("save",):
        usage(cmd, f"Unknown mode '{mode}'")
    result = subprocess.run(
        ['tmux', 'list-windows', '-F', '"#{window_layout}"'],
        capture_output=True, text=True
    )
    windows = []
    windows_str = result.stdout.strip('\n')
    for window_str in windows_str.split('\n'):
        window = {}
        checksum: int = int(window_str[1:5], 16)
        window_str = window_str[6:-1]
        # -Eat until pane delimiter
        while window_str[0] != '[':
            window_str = window_str[1:]
        window_str = window_str[1:]
        #print(f"Before pane: {window_str}")
        # -Panes
        panes = []
        parent: dict | None = None
        while len(window_str) > 0:
            if window_str[0] == '{':
                parent = panes[-1]
                parent['children'] = []
                window_str = window_str[1:]
            elif window_str[0] == '}':
                parent = None
                window_str = window_str[2:]
            offset, pane = parse_pane(window_str)
            window_str = window_str[offset:]
            if parent:
                parent['children'].append(pane)
            else:
                panes.append(pane)
        print(panes)


## Body
if __name__ == "__main__":
    _entry()
