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
    """
    Represents a directed connection between two Zones.

    Attributes:
        target (Zone): The destination Hub/Zone of this link.
        capacity (int): Maximum number of drones allowed on this link
        simultaneously.
        occupancy (int): Current number of drones traversing this link.
    """
    def __init__(self, link: "Zone", link_capacity: int) -> None:
        self.target = link
        self.capacity = link_capacity
        self.occupancy = 0

    def populate(self) -> None:
        """Increments the link occupancy as a drone enters the path."""
        self.occupancy += 1

    def free(self) -> None:
        """Decrements the link occupancy as a drone exits the path."""
        self.occupancy -= 1

    def free_spaces(self) -> int:
        """Returns the remaining available capacity on this link."""
        return self.capacity - self.occupancy


class Zone(ABC):
    """
    Abstract base class representing a Hub (Node) in the simulation graph.

    Attributes:
        name (str): Unique identifier for the hub.
        coordinates (tuple): (x, y) position for visual representation.
        hub_type (HubType): Classification (start, middle, or end).
        zone_type (ZoneTypes): Operational constraints (priority, restricted,
        etc.).
        cost (int): The time/turn weight required to traverse this hub.
        links (List[Link]): List of outgoing connections from this hub.
        occupancy (int): Current count of drones residing at or reserved for
        this hub.
        capacity (int): Total drone capacity allowed at this hub.
    """
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
        """Update the color of the zone"""
        self.color = color

    def update_zone_type(self, zone_type: str) -> None:
        """Update the zone type and cost"""
        self.zone_type = ZoneTypes(zone_type)
        self.cost = 2 if zone_type == "restricted" else 1

    def update_capacity(self, capacity: int) -> None:
        """Update zone capacity"""
        self.capacity = capacity

    def populate(self) -> None:
        """Increments hub occupancy or reservation count."""
        self.occupancy += 1

    def free(self) -> None:
        """Decrements hub occupancy when a drone vacates the zone."""
        self.occupancy -= 1

    def free_spaces(self) -> int:
        """Calculates available slots based on capacity and current
        occupancy."""
        return self.capacity - self.occupancy

    def add_link(self, link: 'Zone', link_capacity: int = 1) -> None:
        """Creates a new directed Link from this hub to a target hub."""
        self.links.append(Link(link, link_capacity))


class StartZone(Zone):
    """
    Specialized Hub representing the simulation's source.

    The capacity is automatically set to the total number of drones
    to accommodate the entire swarm at t=0.
    """
    def __init__(self, name: str, x: int, y: int,
                 total_drones: int, zone: str = "normal",
                 color: str | None = None) -> None:
        super().__init__(name, x, y, zone, color)
        self.hub_type = HubType("start")
        self.zone_occupancy = total_drones
        self.is_movable = True
        self.capacity = total_drones


class EndZone(Zone):
    """
    Specialized Hub representing the simulation's goal.

    Acts as a sink for drones. The simulation typically terminates
    when the occupancy of this zone equals the total drone count.
    """
    def __init__(self, name: str, x: int, y: int,
                 total_drones: int, zone: str = "normal",
                 color: str | None = None) -> None:
        super().__init__(name, x, y, zone, color)
        self.hub_type = HubType("end")
        self.is_movable = True
        self.capacity = total_drones
