from typing import Dict, List
from abc import ABC, abstractmethod
# from pydantic import BaseModel
from srcs.GraphConstructor import Zone


class Drone:
    pass


class Simulator(ABC):
    def __init__(self, graph: Dict[str, Zone],
                 valid_paths: List[str], drones: int) -> None:
        self.graph = graph
        self.valid_paths = valid_paths
        self.drones = drones

    @abstractmethod
    def start_simulation(self):
        pass


class SimulatorOne(Simulator):
    def start_simulation(self):
        path1 = self.valid_paths[0].split(", ")
        for path in path1[: -1]:
            print(self.graph[path].name)


class SimulatorManager:
    pass
