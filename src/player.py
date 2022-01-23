#!/usr/bin/env python3

from enum import Enum, auto

class Token(Enum):
    BOBAIL = auto()
    RED = auto()
    GREEN = auto()
    EMPTY = auto()

class Player(Enum):
    RED = auto()
    GREEN = auto()
