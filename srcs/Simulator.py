from typing import Dict, List
from abc import ABC, abstractmethod
# from pydantic import BaseModel
from srcs.GraphConstructor import Zone
from srcs.helpers import get_pos_obj


class Drone:
    def __init__(self, drone_id: int, start_pos: Zone) -> None:
        self.name = f"D{drone_id}"
        self.pos = start_pos

    def update_pos(self, curr_pos: Zone):
        self.pos = curr_pos


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
        return all_drones

    @abstractmethod
    def start_simulation(self):
        pass


# D1-Junction, D2-Junction
# D1-path_b, D2-path_a, D3-Junction
# D1-goal, D2-goal, D3-path_a
# D3-goal

class SimulatorOne(Simulator):
    def start_simulation(self):
        move_counter = 0
        while (self.end.occupancy < len(self.drones)):
            drone_move = ""
            for drone in self.drones:
                for link in drone.pos.links:
                    # print(drone.name, link.occupancy, link.target.name)
                    if link.is_free() and\
                       link.occupancy <= link.target.capacity:
                        link.populate()
                        drone.pos.free()
                        break

            for drone in self.drones:
                for link in drone.pos.links:
                    if link.occupancy > 0:
                        link.free()
                        link.target.populate()
                        drone.update_pos(link.target)
                        drone_move += f"{drone.name}-{drone.pos.name} "
                        break
            print(drone_move)
            move_counter += 1
        print(f"Total Moves: {move_counter}")


class SimulatorManager:
    pass
