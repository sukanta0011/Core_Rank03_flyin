from typing import Dict, List
import time
from abc import ABC, abstractmethod
# from pydantic import BaseModel
from srcs.parser.GraphConstructor import Zone, Link
from srcs.simulator.helpers import get_pos_obj


class Drone:
    def __init__(self, drone_id: int, start_pos: Zone) -> None:
        self.name = f"D{drone_id}"
        self.pos = start_pos
        self.last_pos: List[float] = list(start_pos.coordinates)
        self.current_pos: List[float] = list(start_pos.coordinates)
        self.target_pos: List[float] = list(start_pos.coordinates)
        self.moves = 0
        self.txt: str = ""
        self.link = None
        self.moving = False

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
        print(f"name: {self.pos.name}({self.name}), "
              f"cost: {self.pos.cost}, move: {self.moves}")
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

    def get_drones(self) -> List[Drone]:
        return self.drones

    def show_zone_state(self):
        zone_state = ""
        for _, zone in self.graph.items():
            zone_state += f"{zone.name}({zone.free_spaces()}:{zone.capacity}) "
        print(f"\n{zone_state}")

    @abstractmethod
    def start_simulation(self, valid_map: Dict[str, List]):
        pass

    @abstractmethod
    def next_move(self, valid_map: Dict[str, List]) -> str:
        pass


class SimpleSimulator(Simulator):
    def get_link_obj(self, link_name: str, links: List[Link]) -> Link | None:
        for link in links:
            if link.target.name == link_name:
                return link
        return None

    def start_simulation(self, valid_map: Dict[str, List]):
        move_counter = 0
        while (self.end.occupancy < len(self.drones)):
            # self.show_zone_state()
            # time.sleep(1)
            drone_move = self.next_move(valid_map)
            # print(drone_move)
            move_counter += 1
            drone_move += f"Move No: {move_counter}"
        print(f"Total Moves: {move_counter}")

    def next_move(self, valid_map: Dict[str, List]) -> str:
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
                            drone.last_pos = list(drone.pos.coordinates)
                            drone.pos.free()
                            drone.increase_move()
                            drone.set_link(link)
                            break

        for drone in self.drones:
            drone.txt = ""
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
                            drone.target_pos = list(drone.pos.coordinates)
                            drone_move += f"{drone.name}-{drone.pos.name} "
                            drone.txt = f"{drone.name}-{drone.pos.name}"
                        # break
                        else:
                            # print(f"{drone.name} is in restricted zone, {drone.link.target.name}")
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
