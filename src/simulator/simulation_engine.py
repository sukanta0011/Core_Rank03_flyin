from typing import Dict, List
from abc import ABC, abstractmethod
# from pydantic import BaseModel
from src.parser.map_constructor import Zone, Link
from src.simulator.helpers import get_pos_obj


class Drone:
    """
    Represents an autonomous agent (drone) within the simulation.

    Manages internal state including current hub position, active transit
    links, and movement telemetry for both logic and visual interpolation.

    Attributes:
        name (str): Unique identifier (e.g., "D1").
        pos (Zone): The current Hub object where the drone is located or
        originated.
        last_pos (List[float]): Coordinates of the hub the drone just vacated.
        target_pos (List[float]): Projected coordinates for visual
        LERP interpolation.
        moves (int): Number of ticks spent on the current link.
        link (Link | None): The active connection the drone is
        currently traversing.
    """
    def __init__(self, drone_id: int, start_pos: Zone) -> None:
        self.name = f"D{drone_id}"
        self.pos = start_pos
        self.last_pos: List[float] = list(start_pos.coordinates)
        self.current_pos: List[float] = list(start_pos.coordinates)
        self.target_pos: List[float] = list(start_pos.coordinates)
        self.waiting_time = 0
        self.moves = 0
        self.total_moves = 0
        self.txt: str = ""
        self.link: Link | None = None
        self.moving = False

    def update_pos(self, curr_pos: Zone) -> None:
        self.pos = curr_pos

    def increase_move(self) -> None:
        self.moves += 1

    def reset_move(self) -> None:
        self.moves = 0

    def set_link(self, link: Link | None) -> None:
        # print(f"Target set: {link.target.name}")
        self.link = link

    def get_link(self) -> Link | None:
        return self.link

    def remaining_moves(self) -> int:
        """Calculates the ticks required to reach the target hub based
        on zone cost."""
        print(f"name: {self.pos.name}({self.name}), "
              f"cost: {self.pos.cost}, move: {self.moves}")
        return self.pos.cost - self.moves


class Simulator(ABC):
    """
    Abstract base class for the drone simulation engine.

    Attributes:
        graph (Dict[str, Zone]): The complete network of hubs and links.
        drones (List[Drone]): The collection of active agents in the
        simulation.
        start (Zone): The designated source hub.
        end (Zone): The designated sink (goal) hub.
    """
    def __init__(self, graph: Dict[str, Zone],
                 valid_paths: List[str], drones: int) -> None:
        self.graph = graph
        self.valid_paths = valid_paths
        self.start = get_pos_obj(graph, "start")
        self.end = get_pos_obj(graph, "end")
        self.drones = self.init_drones(drones)

    def init_drones(self, drones: int) -> List[Drone]:
        """Instantiates drones and populates the start zone with initial
        occupancy."""
        all_drones = []
        if self.start is not None:
            for i in range(1, drones + 1):
                all_drones.append(Drone(i, self.start))
                self.start.populate()
        return all_drones

    def get_drones(self) -> List[Drone]:
        return self.drones

    def show_zone_state(self) -> None:
        zone_state = ""
        for _, zone in self.graph.items():
            zone_state += f"{zone.name}({zone.free_spaces()}:{zone.capacity}) "
        print(f"\n{zone_state}")

    def get_link_obj(self, link_name: str, links: List[Link]) -> Link | None:
        for link in links:
            if link.target.name == link_name:
                return link
        return None

    @abstractmethod
    def start_simulation(self, valid_map: Dict[str, List]) -> None:
        """Core loop that runs until all drones reach the end zone."""
        pass

    @abstractmethod
    def next_move(self, valid_map: Dict[str, List]) -> str:
        pass


class SimpleSimulator(Simulator):
    """
    A basic implementation of the drone simulation engine.

    This simulator follows a deterministic, first-available-path logic.
    It processes drones sequentially and only allows movement if both
    the link and the target hub have immediate free capacity.
    """
    def start_simulation(self, valid_map: Dict[str, List]) -> None:
        """
        Executes the main simulation loop.

        Continues iterating until the number of drones that have reached
        the 'end' hub equals the total swarm size. Increments a global
        move counter for each simulation tick.

        Args:
            valid_map: Adjacency list mapping hub names to their
                       prioritized next-step options.
        """
        move_counter = 0
        if self.end is not None:
            while (self.end.occupancy < len(self.drones)):
                drone_move = self.next_move(valid_map)
                move_counter += 1
                drone_move += f"Move No: {move_counter}"
            print(f"Total Moves: {move_counter}")

    def next_move(self, valid_map: Dict[str, List]) -> str:
        """
        Calculates the state transition for a single simulation tick.

        Phase 1: Entry Logic
        Iterates through all drones. If a drone is at a hub, it attempts
        to enter the first available link from the valid_map.

        Phase 2: Transit Logic
        Iterates through all drones. If a drone is currently in a link,
        it advances its 'moves' counter. If the movement cost is met,
        the drone is 'committed' to the target hub.

        Returns:
            str: A formatted string containing the movement telemetry
                 for the current tick (used for logging or GUI display).
        """
        drone_move = ""
        for drone in self.drones:
            # print(valid_map[drone.pos.name])
            for hub_name in valid_map[drone.pos.name]:
                link = self.get_link_obj(hub_name, drone.pos.links)
                # print(drone.name, link.occupancy, link.target.name)
                if link is not None:
                    if drone.get_link() is not None:
                        # print(f"{drone.name} is in transit")
                        drone.increase_move()
                        drone.total_moves += 1
                        break
                    elif link.free_spaces() > 0:
                        if link.free_spaces() <= link.target.free_spaces():
                            link.populate()
                            drone.last_pos = list(drone.pos.coordinates)
                            drone.pos.free()
                            drone.increase_move()
                            drone.set_link(link)
                            drone.total_moves += 1
                            break

        for drone in self.drones:
            drone.txt = ""
            for link in drone.pos.links:
                temp_link = drone.get_link()
                if link.occupancy > 0 and temp_link is not None:
                    if link.target.name == temp_link.target.name:
                        # print(f"{drone.name}, {link.target.name},
                        #       Cost: {link.target.cost}, Move: {drone.moves}")
                        if (link.target.cost - drone.moves) == 0:
                            drone.reset_move()
                            # print(f"{drone.name} is in restricted zone")
                            link.free()
                            link.target.populate()
                            drone.set_link(None)
                            drone.update_pos(link.target)
                            drone.target_pos = list(drone.pos.coordinates)
                            drone_move += f"{drone.name}-{drone.pos.name} "
                            drone.txt = f"{drone.name}-{drone.pos.name}"
                        # break
                        else:
                            # print(f"{drone.name} is in restricted zone,"
                            #       f"{drone.link.target.name}")
                            drone.target_pos = [drone.last_pos[i] +
                                                (link.target.coordinates[i] -
                                                drone.pos.coordinates[i]) *
                                                (drone.moves /
                                                link.target.cost)
                                                for i in range(2)]
                            drone_move += f"{drone.name}-{drone.pos.name}"\
                                          f"-{link.target.name} "
                            drone.txt = f"{drone.name}-{drone.pos.name}"\
                                        f"-{link.target.name}"
        return drone_move


class AdvanceSimulator(Simulator):
    """
    An optimized simulation engine utilizing back pressure and look-ahead
    logic.

    This simulator improves throughput by allowing drones to move into zones
    simultaneously as they are being vacated by other agents.
    """
    def start_simulation(self, valid_map: Dict[str, List]) -> None:
        """
        Executes the main simulation loop.

        Continues iterating until the number of drones that have reached
        the 'end' hub equals the total swarm size. Increments a global
        move counter for each simulation tick.

        Args:
            valid_map: Adjacency list mapping hub names to their
                       prioritized next-step options.
        """
        move_counter = 0
        if self.end is not None:
            while (self.end.occupancy < len(self.drones)):
                drone_move = self.next_move(valid_map)
                move_counter += 1
                drone_move += f"Move No: {move_counter}"
            print(f"Total Moves: {move_counter}")

    def _set_drone_params(self, link: Link, drone: Drone) -> None:
        """
        Internal helper to atomically update drone telemetry and reserve
        capacity in both the link and the target hub.
        """
        link.populate()
        drone.last_pos = list(drone.pos.coordinates)
        drone.pos.free()
        drone.increase_move()
        drone.set_link(link)
        drone.total_moves += 1
        drone.waiting_time = 0
        link.target.populate()

    def next_move(self, valid_map: Dict[str, List]) -> str:
        """
        Orchestrates the 'Look-Ahead' turn logic.
        1. Identifies zones to be freed this tick via 'zone_to_be_freed'.
        2. Executes movements for drones in transit.
        3. Assigns new links to stationary drones based on immediate
           availability or predicted vacancies.
        """
        drone_move = ""
        # looking ahead and deciding which nodes going to be free
        zone_to_be_freed = set()
        for drone in self.drones:
            for hub_name in valid_map[drone.pos.name]:
                link = self.get_link_obj(hub_name, drone.pos.links)
                # print(drone.name, link.occupancy, link.target.name)
                if link is not None:
                    if drone.get_link() is not None:
                        break
                    elif link.free_spaces() > 0 or \
                            hub_name in zone_to_be_freed:
                        if link.free_spaces() <= link.target.free_spaces():
                            zone_to_be_freed.add(drone.pos.name)
                            break
        # print(zone_to_be_freed)

        for drone in self.drones:
            drone.waiting_time += 1
            for hub_name in valid_map[drone.pos.name]:
                link = self.get_link_obj(hub_name, drone.pos.links)
                # print(drone.name, link.free_spaces(), link.target.name)
                if link is not None:
                    if drone.get_link() is not None:
                        # print(f"{drone.name} is in transit")
                        drone.increase_move()
                        drone.total_moves += 1
                        drone.waiting_time = 0
                        break
                    elif link.free_spaces() > 0:
                        if min(link.free_spaces(),
                               link.target.free_spaces()) > 0:
                            if link.target.name in zone_to_be_freed:
                                zone_to_be_freed.remove(link.target.name)
                            self._set_drone_params(link, drone)
                            break
                        elif link.target.name in zone_to_be_freed:
                            if link.target.name in zone_to_be_freed:
                                zone_to_be_freed.remove(link.target.name)
                            self._set_drone_params(link, drone)
                            break

        for drone in self.drones:
            drone.txt = ""
            for link in drone.pos.links:
                temp_link = drone.get_link()
                if link.occupancy > 0 and temp_link is not None:
                    if link.target.name == temp_link.target.name:
                        # print(f"{drone.name}, {link.target.name}, Cost:"
                        #       f" {link.target.cost}, Move: {drone.moves}")
                        if (link.target.cost - drone.moves) == 0:
                            drone.reset_move()
                            # print(f"{drone.name} is in restricted zone")
                            link.free()
                            # link.target.populate()
                            drone.set_link(None)
                            drone.update_pos(link.target)
                            drone.target_pos = list(drone.pos.coordinates)
                            drone_move += f"{drone.name}-{drone.pos.name} "
                            drone.txt = f"{drone.name}-{drone.pos.name}"
                        # break
                        else:
                            # print(f"{drone.name} is in restricted zone,"
                            #       f"{drone.link.target.name}")
                            drone.target_pos = [drone.last_pos[i] +
                                                (link.target.coordinates[i] -
                                                drone.pos.coordinates[i]) *
                                                (drone.moves /
                                                link.target.cost)
                                                for i in range(2)]
                            drone_move += f"{drone.name}-{drone.pos.name}"\
                                          f"-{link.target.name} "
                            drone.txt = f"{drone.name}-{drone.pos.name}"\
                                        f"-{link.target.name}"
                # else:
                #     print(f"Error: {drone.name} is waiting")
        return drone_move
