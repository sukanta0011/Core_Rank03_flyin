from typing import Tuple
from dataclasses import dataclass


@dataclass
class Color:
    WHITE = 0xFFFFFFFF
    BLACK = 0xFF000000
    PRIORITY = 0xFF00FF00
    RESTRICTED = 0xFF0000FF
    NORMAL = 0xFFFFFFFF
    BLOCKED = 0xFFFF0000


@dataclass
class KeyMap:
    """Data class to to store multiple keys for a specific action"""
    MOVE: Tuple[int, int] = (49, 65436)  # Key '1' and NumPad '1'
    AUTO: Tuple[int, int] = (50, 65433)  # Key '2' and NumPad '2'
    STOP: Tuple[int, int] = (51, 65435)  # Key '3' and NumPad '3'
    QUIT: Tuple[int, int] = (52, 65430)  # Key '4' and NumPad '4'
