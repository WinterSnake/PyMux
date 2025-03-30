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
    print(session)


## Body
if __name__ == "__main__":
    _entry()
