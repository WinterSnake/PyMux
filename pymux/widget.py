##-------------------------------##
## PyMux Session                 ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Widget                        ##
##-------------------------------##

## Imports
from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Literal

## Constants
ORIENTATION = Literal["horizontal", "vertical"] | None
NEST_ORIENTATION: dict[str, tuple[ORIENTATION, str]] = {
    '[': ('horizontal', ']'),
    '{': ('vertical', '}'),
}


## Functions
def calculate_checksum(source: str) -> int:
    """Calculate widget checksum from given source"""
    checksum: int = 0
    for c in source:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum = (checksum + ord(c)) & 0xFFFF
    return checksum


def _parse_widget(source: str) -> tuple[str, Widget]:
    """Parse a tmux source string into a nested widget"""
    source, area = _parse_dimensions(source)
    # -Id
    if source[0] == ',':
        source, _id = _parse_int(source[1:])
        return (source, Widget(_id, area))
    # -Nested Children
    children = []
    orientation, end = NEST_ORIENTATION[source[0]]
    source, child = _parse_widget(source[1:])
    children.append(child)
    while source[0] == ',':
        source, child = _parse_widget(source[1:])
        children.append(child)
    assert source[0] == end
    return (source[1:], Widget(None, area, orientation, children))


def _parse_dimensions(source: str) -> tuple[str, Rectangle]:
    """Parse widget dimensions from tmux source string {x, y, w, h}"""
    source, width = _parse_int(source)
    assert source[0] == 'x'
    source, height = _parse_int(source[1:])
    assert source[0] == ','
    source, x = _parse_int(source[1:])
    assert source[0] == ','
    source, y = _parse_int(source[1:])
    return (source, Rectangle(x, y, width, height))


def _parse_int(source: str) -> tuple[str, int]:
    """Returns parsed integer"""
    value: str = ''
    while len(source) > 0 and source[0].isdigit():
        value += source[0]
        source = source[1:]
    return (source, int(value))


## Classes
class Rectangle:

    # -Constructor
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

    # -Properties
    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        self.x = value[0]
        self.y = value[1]

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self.width = value[0]
        self.height = value[1]


class Widget:
    """
    Tmux Widget 
    Represents a tmux window or a pane in a singular class
    Uses orientation nesting to accomplish pane divisions inside a window widget
    """

    # -Constructor
    def __init__(
        self, _id: int | None, area: Rectangle,
        orientation: ORIENTATION = None, children: Iterable[Widget] | None = None
    ) -> None:
        self.id: int | None = _id
        self.area: Rectangle = area
        self.orientation: ORIENTATION = orientation
        self.children: Iterable[Widget] | None = children
        self.name: str | None = None

    # -Dunder Methods
    def __str__(self) -> str:
        _str = f"{self.area.width}x{self.area.height},{self.area.x},{self.area.y}"
        if not self.children:
            return _str + f",{self.id}"
        # -Children
        assert self.orientation is not None
        children = ','.join(str(child) for child in self.children)
        start, end = {
            'horizontal': ('[', ']'),
            'vertical': ('{', '}'),
        }[self.orientation]
        return _str + start + children + end

    # -Static Methods
    @staticmethod
    def from_layout(layout: str) -> Widget:
        '''Return a widget from a layout string with checksum validation'''
        checksum = int(layout[:4], 16)
        source = layout[5:]
        calculated_checksum = calculate_checksum(source)
        if calculated_checksum != checksum:
            raise ValueError(f"Checksum failed, expected: {checksum:04X}; actual: {calculated_checksum:04X}")
        return _parse_widget(source)[1]

    @staticmethod
    def from_str(source: str) -> Widget:
        '''Return a widget from a layout string without checksum'''
        return _parse_widget(source)[1]

    # -Properties
    @property
    def layout(self) -> str:
        return f"{calculate_checksum(str(self)):04x},{str(self)}"
