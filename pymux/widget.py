#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Widget                        ##
##-------------------------------##

## Imports
from __future__ import annotations
from typing import Literal

## Constants
__all__: tuple[str, ...] = ("Widget", "calculate_checksum", "parse_widget")
type ORIENTATION = Literal["horizontal", "vertical"] | None


## Functions
def calculate_checksum(source: str) -> int:
    """Calculate widget checksum from given source"""
    checksum: int = 0
    for c in source:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += ord(c)
    return checksum


def parse_widget(source: str) -> Widget:
    """Parse tmux layout string into Widget"""
    return _parse_widget(source, 0)[1]


def _parse_widget(source: str, offset: int) -> tuple[int, Widget]:
    """Parse tmux widget structure with id or nesting"""
    offset, obj = _parse_dimensions(source, offset)
    # -Id
    if source[offset] == ',':
        offset, obj._id = _parse_int(source, offset + 1)
    # -Nest: Vertical
    elif source[offset] == '[':
        obj.orientation = "vertical"
        while source[offset] != ']':
            offset, child = _parse_widget(source, offset + 1)
            obj.children.append(child)
        offset += 1
    # -Nest: Horizontal
    elif source[offset] == '{':
        obj.orientation = "horizontal"
        while source[offset] != '}':
            offset, child = _parse_widget(source, offset + 1)
            obj.children.append(child)
        offset += 1
    return (offset, obj)


def _parse_dimensions(source: str, offset: int) -> tuple[int, Widget]:
    """Parse tmux widget dimensions (x, y, w, h)"""
    offset, width = _parse_int(source, offset)
    offset, height = _parse_int(source, offset + 1)
    offset, x = _parse_int(source, offset + 1)
    offset, y = _parse_int(source, offset + 1)
    return (offset, Widget((x, y), (width, height)))


def _parse_int(source: str, offset: int) -> tuple[int, int]:
    """Parse int from source"""
    value: int = 0
    while len(source) > offset and (c := source[offset]).isdigit():
        value = value * 10 + int(c)
        offset += 1
    return (offset, value)


## Classes
class Widget:
    """
    Tmux Window/Pane
    Represents a window or a pane in a singular class
    """

    # -Constructor
    def __init__(
        self, position: tuple[int, int], size: tuple[int, int],
        orientation: ORIENTATION = None,
    ) -> None:
        self._id: int | None = None
        # -Dimensions
        self.position: tuple[int, int] = position
        self.size: tuple[int, int] = size
        # -Children
        self.orientation: ORIENTATION = orientation
        self.children: list[Widget] = []

    # -Dunder Methods
    def __str__(self) -> str:
        widget: str = f"{self.width}x{self.height},{self.x},{self.y}"
        if not self.children:
            return widget + f",{self.id}"
        if self.orientation == 'horizontal':
            widget += '{'
        else:
            widget += '['
        for i, child in enumerate(self.children):
            widget += str(child)
            if i < len(self.children) - 1:
                widget += ','
        if self.orientation == 'horizontal':
            widget += '}'
        else:
            widget += ']'
        return widget

    # -Class Methods
    @classmethod
    def from_layout(cls, source: str) -> Widget:
        '''Create a widget from a given tmux layout string with checksum validation'''
        checksum = int(source[:4], 16)
        source = source[5:]
        assert checksum == calculate_checksum(source)
        return parse_widget(source)

    # -Properties
    @property
    def id(self) -> int:
        return self._id if self._id is not None else 0

    @property
    def layout(self) -> str:
        return f"{calculate_checksum(str(self)):4x},{self}"

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
