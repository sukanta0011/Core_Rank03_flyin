from typing import List, Optional
from enum import Enum
from abc import ABC


class ZoneTypes(Enum):
    priority = "priority"
    normal = "normal"
    restricted = "restricted"
    blocked = "blocked"


class HubType(Enum):
    start = "start"
    end = "end"
    middle = "middle"


class Link:
    def __init__(self, link: "Zone", link_capacity: int) -> None:
        self.target = link
        self.capacity = link_capacity
        self.occupancy = 0

    def populate(self) -> None:
        self.occupancy += 1

    def free(self) -> None:
        self.occupancy -= 1

    def free_spaces(self) -> int:
        return self.capacity - self.occupancy


class Zone(ABC):
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal",
                 color: Optional[str] = None,
                 capacity: int = 1) -> None:
        self.name = name
        self.coordinates = (x, y)
        self.hub_type = HubType("middle")
        self.zone_type = ZoneTypes(zone_type)
        self.color = color
        self.cost = 2 if zone_type == "restricted" else 1
        self.moves = 0
        self.links: List[Link] = []
        self.occupancy = 0
        self.is_movable = False
        self.capacity = capacity

    def update_color(self, color: str) -> None:
        self.color = color

    def update_zone(self, zone_type: str) -> None:
        self.zone_type = ZoneTypes(zone_type)
        self.cost = 2 if zone_type == "restricted" else 1

    def update_capacity(self, capacity: int) -> None:
        self.capacity = capacity

    def populate(self) -> None:
        self.occupancy += 1

    def free(self) -> None:
        self.occupancy -= 1

    def free_spaces(self) -> int:
        return self.capacity - self.occupancy

    def add_link(self, link: 'Zone', link_capacity: int = 1) -> None:
        self.links.append(Link(link, link_capacity))


class StartZone(Zone):
    def __init__(self, name: str, x: int, y: int,
                 total_drones: int, zone: str = "normal",
                 color: str | None = None) -> None:
        super().__init__(name, x, y, zone, color)
        self.hub_type = HubType("start")
        self.zone_occupancy = total_drones
        self.is_movable = True
        self.capacity = total_drones


class EndZone(Zone):
    def __init__(self, name: str, x: int, y: int,
                 total_drones: int, zone: str = "normal",
                 color: str | None = None) -> None:
        super().__init__(name, x, y, zone, color)
        self.hub_type = HubType("end")
        self.is_movable = True
        self.capacity = total_drones
