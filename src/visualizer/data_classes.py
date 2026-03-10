from typing import Tuple
from dataclasses import dataclass


@dataclass
class Color:
    """
    Hexadecimal color constants for MiniLibX rendering.

    Values are stored in 0xAARRGGBB or 0xRRGGBB format depending on
    the MLX configuration.

    Attributes:
        PRIORITY (int): Green - Highlights optimal or high-value paths.
        RESTRICTED (int): Blue - Indicates zones with higher movement costs.
        BLOCKED (int): Red - Designates non-traversable hubs.
    """
    WHITE = 0xFFFFFFFF
    BLACK = 0xFF000000
    PRIORITY = 0xFF00FF00
    RESTRICTED = 0xFF0000FF
    NORMAL = 0xFFFFFFFF
    BLOCKED = 0xFFFF0000


@dataclass
class KeyMap:
    """
    Standardizes input handling across different keyboard layouts.

    Each attribute stores a tuple containing the standard ASCII keycode
    and its corresponding NumPad equivalent to ensure cross-hardware
    compatibility.

    Attributes:
        MOVE (tuple): Triggers a single manual simulation tick.
        AUTO (tuple): Activates the continuous simulation loop.
        STOP (tuple): Pauses the automated simulation.
        QUIT (tuple): Safely terminates the visualizer and closes windows.
    """
    MOVE: Tuple[int, int] = (49, 65436)  # Key '1' and NumPad '1'
    AUTO: Tuple[int, int] = (50, 65433)  # Key '2' and NumPad '2'
    STOP: Tuple[int, int] = (51, 65435)  # Key '3' and NumPad '3'
    QUIT: Tuple[int, int] = (52, 65430)  # Key '4' and NumPad '4'
