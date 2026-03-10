from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
from src.parser.map_constructor import Zone
if TYPE_CHECKING:
    from src.visualizer.map_visualizer import ConstantParameters


def get_pos_obj(graph: Dict[str, Zone],
                pos_name: str) -> Zone | None:
    """
    Searches the graph for a Zone matching a specific HubType value
    (e.g., 'start' or 'end').

    Args:
        graph: Dictionary mapping hub names to Zone objects.
        pos_name: The string value of the HubType to search for.
    Returns:
        The first matching Zone object, or None if not found.
    """
    for _, v in graph.items():
        if v.hub_type.value == pos_name:
            return v
    return None


def format_valid_paths_into_list(paths: List[str]) -> List[List[str]]:
    """
    Converts raw comma-separated path strings into a nested list structure.

    This prepares the DFS output for easier indexing and sorting.
    """
    new_paths = []
    for path in paths:
        path_list = path.split(", ")
        # path_list[-1] = float(path_list[-1])
        new_paths.append(path_list)
    return new_paths


def create_valid_graph(hubs_name: List[str],
                       paths: List[List]) -> Dict[str, List[str]]:
    """
    Generates an adjacency-style 'Priority Map'.

    For every hub, it identifies all possible next steps found in valid paths.
    Paths are sorted by cost (last element of path list) to ensure that
    higher-efficiency options appear earlier in the adjacency list.
    """
    priority_paths: Dict[str, List[str]] = {}
    sorted_paths = sorted(paths, key=lambda path: float(path[-1]))
    # print(sorted_paths)
    for hub in hubs_name:
        priority_paths[hub] = []
        for path in sorted_paths:
            try:
                idx = path.index(hub)
                if len(path) > idx + 2:
                    if path[idx + 1] not in priority_paths[hub]:
                        priority_paths[hub].append(path[idx + 1])
            except ValueError:
                pass
    # print(priority_paths)
    return priority_paths


def create_reverse_valid_graph(hubs_name: List[str],
                               paths: List[List],
                               map: Dict[str, Zone]) -> Dict[str, List[str]]:
    """
    It create a map in reverse order starting from the goal to the start.
    It generates connections that leads to the next hub.
    """
    priority_paths: Dict[str, List[str]] = {}
    sorted_paths = sorted(paths, key=lambda path: float(path[-1]))
    # print(sorted_paths)
    for hub in reversed(hubs_name):
        priority_paths[hub] = []

    for hub in reversed(hubs_name):
        priority_paths[hub] = []
        for path in sorted_paths:
            try:
                hub_idx = path.index(hub)
                if (hub_idx > 0 and
                   path[hub_idx - 1] not in priority_paths[hub]):
                    priority_paths[hub].append(path[hub_idx - 1])
            except ValueError:
                pass
    # print(priority_paths)
    return priority_paths

# def create_reverse_valid_graph(
#         valid_map: Dict[str, List[str]],
#         map: Dict[str, Zone]) -> Dict[str, List[str]]:
#     rev_map: Dict[str, List[str]] = {}
#     print(valid_map)
#     for key, val in reversed(valid_map.items()):
#         rev_map[key] = []

#     for key, val in reversed(valid_map.items()):
#         for item in val:
#             if item in rev_map.keys():
#                 rev_map[item].append(key)
#     # print(rev_map)
#     return rev_map


def sort_map_by_priority(valid_map: Dict[str, List[str]],
                         map: Dict[str, Zone]) -> Dict[str, List[str]]:
    """
    Re-orders the adjacency list for each hub based on ZoneType.

    If a target hub is marked as a 'priority' zone, it is moved to the front
    of the list, overriding the default cost-based sorting.
    """
    for _, val in valid_map.items():
        priority_list = []
        for hub in val:
            if map[hub].zone_type.value == "priority":
                priority_list.append(hub)
        for item in reversed(priority_list):
            val.remove(item)
            val.insert(0, item)

    # print(valid_map)
    return valid_map


def get_min_max_coordinates_from_map(
        map: Dict[str, Zone]) -> Tuple[int, int, int, int]:
    """Return the minimum and the maximum coordinate x and y
    in a provided map"""
    x_coords = [val.coordinates[0] for _, val in map.items()]
    y_coords = [val.coordinates[1] for _, val in map.items()]
    return (min(x_coords), max(x_coords),
            min(y_coords), max(y_coords))


def calculate_window_size(
        const: ConstantParameters,
        boundary: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """
    Dynamically calculates the MLX window dimensions based on map coordinates.

    Uses the min/max coordinates and a multiplier (mul) to ensure the entire
    graph fits on screen with appropriate offsets and padding.
    """
    x_max = boundary[1] * const.mul + const.x_offset
    if x_max > const.win_w:
        const.win_w = x_max + const.sq_len * 2
    # y_min = boundary[2] * const.mul + const.y_offset
    y_max = (boundary[3] - boundary[2]) * const.mul +\
        const.y_offset + const.sq_len * 3
    # print(boundary, x_max, y_max)
    if y_max > const.win_h:
        const.win_h = y_max + const.sq_len * 3
    const.y_cent = const.y_offset + \
        int((const.win_h - const.y_offset) * ((abs(boundary[2]) + 2) /
            (abs(boundary[3]) + abs(boundary[2]) + 3.5)))
    return (const.win_w, const.win_h)
