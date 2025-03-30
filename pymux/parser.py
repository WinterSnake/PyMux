#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Layout Parser                 ##
##-------------------------------##


## Functions
def parse_layout(source: str) -> dict:
    """
    Parse layout string into nested structure
    """
    return _parse_object(source, 0)[1]


def _parse_object(source: str, offset: int) -> tuple[int, dict]:
    """
    Parse window/pane structure with id or nesting
    """
    offset, obj = _parse_dimensions(source, offset)
    # -Id
    if source[offset] == ',':
        offset, obj['id'] = _parse_int(source, offset + 1)
    # -Nest: Vertical
    elif source[offset] == '[':
        children = []
        while source[offset] != ']':
            offset, child = _parse_object(source, offset + 1)
            children.append(child)
        offset += 1
        obj.update({ 'orientation': "vertical", 'children': children})
    # -Nest: Horizontal
    elif source[offset] == '{':
        children = []
        while source[offset] != '}':
            offset, child = _parse_object(source, offset + 1)
            children.append(child)
        offset += 1
        obj.update({ 'orientation': "horizontal", 'children': children})
    return (offset, obj)


def _parse_dimensions(source: str, offset: int) -> tuple[int, dict]:
    """
    Parse window/pane dimensions (x, y, w, h)
    """
    offset, width = _parse_int(source, offset)
    offset, height = _parse_int(source, offset + 1)
    offset, x = _parse_int(source, offset + 1)
    offset, y = _parse_int(source, offset + 1)
    return (offset, { 'pos': (x, y), 'size': (width, height) })


def _parse_int(source: str, offset: int) -> tuple[int, int]:
    """
    Parse int from text
    """
    value: int = 0
    while len(source) > offset and (c := source[offset]).isdigit():
        value = value * 10 + int(c)
        offset += 1
    return (offset, value)
