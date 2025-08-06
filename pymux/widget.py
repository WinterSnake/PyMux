##-------------------------------##
## PyMux Session                 ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Widget                        ##
##-------------------------------##

## Imports
from __future__ import annotations
from collections.abc import Iterable
from typing import Literal

## Constants
ORIENTATION = Literal["horizontal"] | Literal["vertical"] | None


## Functions
def calculate_checksum(source: str) -> int:
    """Calculate widget checksum from given source"""
    checksum: int = 0
    for c in source:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum = (checksum + ord(c)) & 0xFFFF
    return checksum

def parse_widget(source: str) -> tuple[str, Widget]:
    """Parse a tmux source string into a nested widget"""
    source, dimensions = _parse_dimensions(source)
    # -Id
    if source[0] == ',':
        source, _id = _parse_int(source[1:])
        return (source, Widget(dimensions, _id))
    # -Nest: Horizontal
    elif source[0] == '{':
        source, children = _parse_children(source[1:])
        widget = Widget(dimensions, None, 'horizontal', children)
        assert source[0] == '}'
        return (source[1:], widget)
    # -Nest: Vertical
    elif source[0] == '[':
        source, children = _parse_children(source[1:])
        widget = Widget(dimensions, None, 'vertical', children)
        assert source[0] == ']'
        return (source[1:], widget)
    raise ValueError(f"Invalid layout string: {source}")


def _parse_children(source: str) -> tuple[str, list[Widget]]:
    """Return all parsed children widgets"""
    children = []
    source, widget = parse_widget(source)
    children.append(widget)
    while source[0] == ',':
        source, widget = parse_widget(source[1:])
        children.append(widget)
    return (source, children)


def _parse_dimensions(source: str) -> tuple[str, tuple[int, int, int, int]]:
    """Parse widget dimensions from tmux source string {x, y, w, h}"""
    source, width = _parse_int(source)
    source, height = _parse_int(source[1:])
    source, x = _parse_int(source[1:])
    source, y = _parse_int(source[1:])
    return (source, (x, y, width, height))


def _parse_int(source: str) -> tuple[str, int]:
    """Returns parsed integer"""
    value: str = ''
    while len(source) > 0 and source[0].isdigit():
        value += source[0]
        source = source[1:]
    return (source, int(value))


## Classes
class Widget:
    """
    Tmux Widget 
    Represents a tmux window or a pane in a singular class
    Uses orientation nesting to accomplish pane divisions inside a window widget
    """

    # -Constructor
    def __init__(
        self, dimensions: tuple[int, int, int, int],
        _id: int | None, orientation: ORIENTATION = None,
        children: Iterable[Widget] | None = None
    ) -> None:
        self.id: int | None = _id
        self.position: tuple[int, int] = (dimensions[0], dimensions[1])
        self.size: tuple[int, int] = (dimensions[2], dimensions[3])
        self.orientation: ORIENTATION = orientation
        self.children: Iterable[Widget] | None = children

    # -Dunder Methods
    def __str__(self) -> str:
        _str = f"{self.width}x{self.height},{self.x},{self.y}"
        # -Id
        if not self.children:
            return _str + f",{self.id}"
        # -Children
        children = ','.join(str(child) for child in self.children)
        if self.orientation == 'horizontal':
            return _str + '{' + children + '}'
        else:
            return _str + '[' + children + ']'

    # -Class Methods
    @classmethod
    def from_layout(cls, layout: str) -> Widget:
        '''Validate widget from a source and return widget'''
        checksum = int(layout[:4], 16)
        source = layout[5:]
        calculated_checksum = calculate_checksum(source)
        if calculated_checksum != checksum:
            raise ValueError(f"Checksum failed, expected: {checksum:04x}; actual: {calculated_checksum:04x}")
        assert calculate_checksum(source) == checksum
        return parse_widget(source)[1]

    # -Properties
    @property
    def layout(self) -> str:
        return f"{calculate_checksum(str(self)):04x},{str(self)}"

    @property
    def x(self) -> int:
        return self.position[0]

    @x.setter
    def x(self, value: int) -> None:
        self.position = (value, self.y)

    @property
    def y(self) -> int:
        return self.position[1]

    @y.setter
    def y(self, value: int) -> None:
        self.position = (self.x, value)

    @property
    def width(self) -> int:
        return self.size[0]

    @width.setter
    def width(self, value: int) -> None:
        self.size = (value, self.height)

    @property
    def height(self) -> int:
        return self.size[1]

    @height.setter
    def height(self, value: int) -> None:
        self.size = (self.width, value)
