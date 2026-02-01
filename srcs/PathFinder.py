from typing import List, Dict
from abc import ABC, abstractmethod
from srcs.GraphConstructor import Zone


class PathFinder(ABC):
    def __init__(self, graph: Dict[str, Zone]) -> None:
        self.graph = graph

    @abstractmethod
    def find_valid_paths(self) -> List[str]:
        pass

    def can_move_forward(self, curr_pos: Zone, path: str) -> bool:
        if len(curr_pos.links) == 0 or\
                curr_pos.name in path or\
                curr_pos.zone_type.value == "restricted":
            return False
        return True

    def is_end(self, curr_pos: Zone) -> bool:
        if curr_pos.hub_type.value == "end":
            return True
        return False


class DepthFirstSearch(PathFinder):
    def find_valid_paths(self):
        valid_paths = []
        path = ""
        cost = -1
        curr_pos = self.graph['start']
        # print(curr_pos.name)
        self._use_recursion(curr_pos, path, cost, valid_paths)
        return valid_paths

    def _use_recursion(self, curr_pos: Zone, path: str,
                       cost: int, valid_paths: List):
        if not self.can_move_forward(curr_pos, path):
            path += f"{curr_pos.name}, "
            cost += curr_pos.cost
            path += str(cost)
            if self.is_end(curr_pos):
                valid_paths.append(path)
            return
        # path.append(curr_pos.name)
        path += f"{curr_pos.name}, "
        cost += curr_pos.cost
        for link in curr_pos.links:
            self._use_recursion(link.target, path, cost, valid_paths)
