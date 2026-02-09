from typing import Dict, List
import time
from abc import ABC, abstractmethod
# from pydantic import BaseModel
from srcs.GraphConstructor import Zone, Link
from srcs.helpers import get_pos_obj


class Drone:
    def __init__(self, drone_id: int, start_pos: Zone) -> None:
        self.name = f"D{drone_id}"
        self.pos = start_pos
        self.moves = 0
        self.link = None

    def update_pos(self, curr_pos: Zone):
        self.pos = curr_pos

    def increase_move(self):
        self.moves += 1

    def reset_move(self):
        self.moves = 0

    def set_link(self, link: Link | None):
        # print(f"Target set: {link.target.name}")
        self.link = link

    def get_link(self) -> Link:
        return self.link

    def remaining_moves(self) -> int:
        print(f"name: {self.pos.name}({self.name}), cost: {self.pos.cost}, move: {self.moves}")
        return self.pos.cost - self.moves


class Simulator(ABC):
    def __init__(self, graph: Dict[str, Zone],
                 valid_paths: List[str], drones: int) -> None:
        self.graph = graph
        self.valid_paths = valid_paths
        self.start = get_pos_obj(graph, "start")
        self.end = get_pos_obj(graph, "end")
        self.drones = self.init_drones(drones)

    def init_drones(self, drones: int) -> List[Drone]:
        all_drones = []
        if self.start is not None:
            for i in range(1, drones + 1):
                all_drones.append(Drone(i, self.start))
                self.start.populate()
        return all_drones

    def show_zone_state(self):
        zone_state = ""
        for _, zone in self.graph.items():
            zone_state += f"{zone.name}({zone.free_spaces()}:{zone.capacity}) "
        print(f"\n{zone_state}")

    @abstractmethod
    def start_simulation(self, valid_map: Dict[str, List]):
        pass


# D1-Junction, D2-Junction
# D1-path_b, D2-path_a, D3-Junction
# D1-goal, D2-goal, D3-path_a
# D3-goal

class SimpleSimulator(Simulator):
    def get_link_obj(self, link_name: str, links: List[Link]) -> Link | None:
        for link in links:
            if link.target.name == link_name:
                return link
        return None

    def start_simulation(self, valid_map: Dict[str, List]):
        move_counter = 0
        while (self.end.occupancy < len(self.drones)):
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
                            break
                        elif link.free_spaces() > 0:
                            if link.free_spaces() <= link.target.free_spaces():
                                link.populate()
                                drone.pos.free()
                                drone.increase_move()
                                drone.set_link(link)
                                break

            for drone in self.drones:
                for link in drone.pos.links:
                    # if link.occupancy > 0 and link.target.zone_type.value == "restricted" and\
                    if link.occupancy > 0 and drone.get_link() is not None:
                        if link.target.name == drone.get_link().target.name:
                            # print(f"{drone.name}, {link.target.name}, Cost: {link.target.cost}, Move: {drone.moves}")
                            if (link.target.cost - drone.moves) == 0:
                                drone.reset_move()
                                # print(f"{drone.name} is in restricted zone")
                                link.free()
                                link.target.populate()
                                drone.set_link(None)
                                drone.update_pos(link.target)
                                drone_move += f"{drone.name}-{drone.pos.name} "
                            # break
                            else:
                                # print(f"{drone.name} is in restricted zone, {drone.link.target.name}")
                                drone_move += f"{drone.name}-{drone.pos.name}"\
                                              f"-{link.target.name} "
            self.show_zone_state()
            print(drone_move)
            move_counter += 1
        print(f"Total Moves: {move_counter}")

class SimulatorManager:
    pass
