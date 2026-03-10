class MapError(Exception):
    """Base class for all exceptions raised during map parsing and
    validation."""
    def __init__(self, line_no: int, msg: str) -> None:
        super().__init__(f"Line {line_no}: {msg}" if line_no > 0 else msg)


class DroneNumError(MapError):
    """Raised when the 'nb_drones' directive is missing,
    invalid, or non-positive."""
    pass


class FormattingError(MapError):
    """Raised for general syntax violations or unknown line
    starters in the map file."""
    pass


class HubError(MapError):
    """Base class for errors related to Hub/Zone definition
    and registration."""
    pass


class CoordinatesError(HubError):
    """Raised when hub coordinates are non-integers, negative,
    or overlapping."""
    pass


class MetadataError(HubError):
    """Base class for errors within the bracketed metadata
    [key=value] section."""
    pass


class ColorError(MetadataError):
    """Raised when a provided color name or hex code cannot be resolved."""
    pass


class ZoneError(MetadataError):
    """Raised when an unrecognized ZoneType (e.g., not 'priority', 'normal')
    is provided."""
    pass


class DroneOccupancyError(MetadataError):
    """Raised when 'max_drones' constraints are violated or logically
    inconsistent."""
    pass


class LinkingError(MapError):
    """Base class for errors involving hub-to-hub connections."""
    pass


class MaxLinkError(LinkingError):
    """Raised when 'max_link_capacity' is missing or set to an
    invalid value."""
    pass
