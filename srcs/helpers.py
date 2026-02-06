from typing import Dict, List
from srcs.GraphConstructor import Zone


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

def create_valid_graph(paths: List[List]):
    path_network = {}
    for path in paths:
        print(path[1])
