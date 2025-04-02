#!/usr/bin/python
##-------------------------------##
## PyMux                         ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Widget                        ##
##-------------------------------##

## Imports
from __future__ import annotations
from typing import ClassVar, Literal, Self

## Constants
type ORIENTATION = Literal['horizontal', 'vertical'] | None


## Functions
def calculate_checksum(source: str) -> int:
    """Calculate widget checksum from given source"""
    checksum: int = 0
    for c in source:
        checksum = (checksum >> 1) + ((checksum & 1) << 15)
        checksum += ord(c)
    return checksum


def _parse_widget(source: str, offset: int) -> tuple[int, Widget]:
    """Parse tmux widget structure with id or nesting"""
    offset, obj = _parse_dimensions(source, offset)
    # -Object Id
    if source[offset] == ',':
        offset, obj._id = _parse_int(source, offset + 1)
    # -Object Nesting: Horizontal
    elif source[offset] == '{':
        obj.orientation = 'horizontal'
        while source[offset] != '}':
            offset, child = _parse_widget(source, offset + 1)
            obj.children.append(child)
        offset += 1
    # -Object Nesting: Vertical
    elif source[offset] == '[':
        obj.orientation = 'vertical'
        while source[offset] != ']':
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
    widget = Widget(x, y, width, height)
    return (offset, widget)


def _parse_int(source: str, offset: int) -> tuple[int, int]:
    """Parse int from source"""
    value: int = 0
    while len(source) > offset and source[offset].isdigit():
        value = value * 10 + int(source[offset])
        offset += 1
    return (offset, value)


## Classes
class Widget:
    """
    Tmux Window/Pane
    Represents a window or a pane in a singular class
    """

    # -Constructor
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self._id: int | None = None
        # -Dimensions
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        # -Children
        self.orientation: ORIENTATION = None
        self.children: list[Widget] = []

    # -Dunder Methods
    def __iter__(self) -> Self:
        self._index: int = 0
        self._index_stack: list[Widget] = self.children[:]
        return self

    def __next__(self) -> Widget:
        if self._index >= len(self):
            raise StopIteration()
        widget: Widget
        if not self.children:
            widget = self
        else:
            while self._index_stack:
                widget = self._index_stack.pop()
                if not widget.children:
                    break
                self._index_stack.extend(widget.children)
        self._index += 1
        return widget

    def __len__(self) -> int:
        if not self.children:
            return 1
        count: int = 0
        child_stack: list[Widget] = self.children[:]
        while child_stack:
            child = child_stack.pop()
            if child.children:
                child_stack.extend(child.children)
            else:
                count += 1
        return count

    def __str__(self) -> str:
        widget: str = f"{self.width}x{self.height},{self.x},{self.y}"
        if not self.children:
            return widget + f",{self.id}"
        children: str = ','.join(str(child) for child in self.children)
        if self.orientation == 'horizontal':
            return widget + '{' + children + '}'
        elif self.orientation == 'vertical':
            return widget + '[' + children + ']'
        raise ValueError("Orientation expected to be 'horizontal' or 'vertical', got: '{self.orientation}'")

    # -Instance Methods
    def find_by_id(self, _id: int) -> Widget | None:
        '''Find a given widget by it's id'''
        if self._id == _id:
            return self
        for child in self.children:
            if (w := child.find_by_id(_id)) is not None:
                return w
        return None

    def sort(self) -> None:
        '''Sort widget and it's children by X/Y'''
        if not self.children:
            return
        self.children.sort(key=lambda k: (k.x, k.y))
        for child in self.children:
            child.sort()

    # -Class Methods
    @classmethod
    def from_layout(cls, source: str) -> Widget:
        '''Create a widget from a given tmux layout string with checksum validation'''
        checksum = int(source[:4], 16)
        source = source[5:]
        assert checksum == calculate_checksum(source)
        return _parse_widget(source, 0)[1]

    # -Properties
    @property
    def id(self) -> int:
        if self._id is None:
            self._id = Widget._Id
            Widget._Id += 1
        return self._id

    @property
    def layout(self) -> str:
        return f"{calculate_checksum(str(self)):04x},{self}"

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

    # -Class Properties
    _Id: ClassVar[int] = 1
