from typing import List, Dict
from abc import ABC, abstractmethod
from src.parser.map_constructor import Zone
from src.simulator.helpers import get_pos_obj


class PathFinder(ABC):
    """
    An abstract base class for graph traversal and path discovery.

    Provides foundational utilities for validating movement constraints
    and identifying terminal states in the drone network.

    Attributes:
        graph (Dict[str, Zone]): The pre-processed graph of hubs to explore.
    """
    def __init__(self, graph: Dict[str, Zone]) -> None:
        self.graph = graph

    @abstractmethod
    def find_valid_paths(self) -> List[str]:
        """Discovers all viable routes from Start to End."""
        pass

    def can_move_forward(self, curr_pos: Zone, path: str) -> bool:
        """
        Validates if a move is permissible based on link availability,
        cycle prevention (visited nodes), and zone type constraints.
        """
        if len(curr_pos.links) == 0 or\
                curr_pos.name in path or\
                curr_pos.zone_type.value == "blocked":
            return False
        return True

    def is_end(self, curr_pos: Zone) -> bool:
        """
        Validates if a move is permissible based on link availability,
        cycle prevention (visited nodes), and zone type constraints.
        """
        if curr_pos.hub_type.value == "end":
            return True
        return False


class DepthFirstSearch(PathFinder):
    """
    Implements a recursive Depth-First Search to find all non-cyclic paths.

    Calculates a weighted cost for each discovered path based on zone type
    penalties and bottleneck capacities.
    """
    def find_valid_paths(self) -> List:
        """
        Initiates the recursive search starting from the 'start' hub.

        Returns:
            List[str]: A list of strings, each representing a full path
                       and its associated total cost.
        """
        valid_paths: List = []
        path = ""
        cost = -1
        link_cap = 1
        curr_pos = get_pos_obj(self.graph, "start")
        if curr_pos is not None:
            self._use_recursion(curr_pos, path, cost, valid_paths,
                                link_cap, curr_pos)
        return valid_paths

    def _use_recursion(self, curr_pos: Zone, path: str,
                       cost: (int | float), valid_paths: List,
                       link_cap: int, last_pos: Zone) -> None:
        """
        Internal recursive worker for path exploration.

        Handles:
        - Path string concatenation.
        - Dynamic cost calculation based on Zone cost and Link capacity.
        - Base-case termination at the 'end' hub or dead-ends.
        - Implicit backtracking via the call stack.
        """
        if not self.can_move_forward(curr_pos, path):
            path += f"{curr_pos.name}, "
            if last_pos.capacity >= link_cap and curr_pos.capacity >= link_cap:
                cost += curr_pos.cost / link_cap
            else:
                cost += curr_pos.cost
            path += str(cost)
            if self.is_end(curr_pos):
                valid_paths.append(path)
            return
        # print(curr_pos.name, last_pos.name)
        path += f"{curr_pos.name}, "
        if last_pos.capacity >= link_cap and curr_pos.capacity >= link_cap:
            cost += curr_pos.cost / link_cap
        else:
            cost += curr_pos.cost
        for link in curr_pos.links:
            link_cap = link.capacity
            self._use_recursion(link.target, path, cost, valid_paths,
                                link_cap, curr_pos)
