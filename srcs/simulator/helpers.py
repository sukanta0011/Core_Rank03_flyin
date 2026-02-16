from typing import Dict, List
from srcs.parser.GraphConstructor import Zone


def get_pos_obj(graph: Dict[str, Zone],
                pos_name: str) -> Zone | None:
    for _, v in graph.items():
        if v.hub_type.value == pos_name:
            return v
    return None


def format_valid_paths_into_list(paths: List[str]) -> List[List]:
    new_paths = []
    for path in paths:
        path_list = path.split(", ")
        path_list[-1] = float(path_list[-1])
        new_paths.append(path_list)
    return new_paths


def create_valid_graph(hubs_name: List[str],
                       paths: List[List]) -> Dict[str, List[str]]:
    priority_paths: Dict[str, List[str]] = {}
    sorted_paths = sorted(paths, key=lambda path: path[-1])
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


def sort_map_by_priority(valid_map: Dict[str, List[str]],
                         map: Dict[str, Zone]) -> Dict[str, List[str]]:
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
