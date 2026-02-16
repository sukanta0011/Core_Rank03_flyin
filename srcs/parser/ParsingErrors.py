class MapError(Exception):
    pass


class DroneNumError(MapError):
    pass


class FormattingError(MapError):
    pass


class HubError(MapError):
    pass


class CoordinatesError(HubError):
    pass


class MetadataError(HubError):
    pass


class ColorError(MetadataError):
    pass


class ZoneError(MetadataError):
    pass


class DroneOccupancyError(MetadataError):
    pass


class LinkingError(MapError):
    pass


class MaxLinkError(LinkingError):
    pass
