from typing import List
import sys
from src.parser.map_parser import MapParser
from src.simulator.path_finder import DepthFirstSearch
from src.simulator.simulation_engine import AdvanceSimulator
from src.visualizer.map_visualizer import ConstantParameters, GraphVisualizer
from src.visualizer.mlx_tools.image_operations import (
    ImageScaler, ImageOperations)
from src.simulator.helpers import (
    format_valid_paths_into_list,
    create_valid_graph,
    sort_map_by_priority,
    get_min_max_coordinates_from_map,
    calculate_window_size,
    )


def all_map_paths(path_no: int) -> str:
    """Return the path matching to the provided path no.

    Args:
        path_no (int): Integer number of the path.

    Returns:
        str: path to the map
    """
    paths: List[str] = [
        "maps/easy/01_linear_path.txt",
        "maps/easy/02_simple_fork.txt",
        "maps/easy/03_basic_capacity.txt",
        "maps/medium/01_dead_end_trap.txt",
        "maps/medium/02_circular_loop.txt",
        "maps/medium/03_priority_puzzle.txt",
        "maps/hard/01_maze_nightmare.txt",
        "maps/hard/02_capacity_hell.txt",
        "maps/hard/03_ultimate_challenge.txt",
        "maps/challenger/01_the_impossible_dream.txt"
    ]
    if path_no > len(paths) - 1:
        print("Path no not correct: Valid path "
              f"no are between 0-{len(paths) - 1}")
        return paths[0]
    return paths[path_no]


def main() -> None:
    try:
        file_path = sys.argv[1] if len(sys.argv) > 1 else "default_map.txt"
        map_parser = MapParser()
        map_parser.parse(file_path)
        # map_parser.show_map()
        drone_counts = map_parser.get_drone_num()
        map = map_parser.get_map()
        if map is not None and drone_counts is not None:
            dfs = DepthFirstSearch(map)
            paths = dfs.find_valid_paths()
            if len(paths) > 0:
                new_paths = format_valid_paths_into_list(paths)
                hubs_name = list(map.keys())
                valid_map = create_valid_graph(hubs_name, new_paths)
                valid_map = sort_map_by_priority(valid_map, map)
                sim = AdvanceSimulator(graph=map, valid_paths=paths,
                                       drones=drone_counts)
                drones = sim.get_drones()
                const = ConstantParameters()
                w, h = calculate_window_size(
                    const, get_min_max_coordinates_from_map(map))
                graph_visual = GraphVisualizer(file_path, map, w, h, valid_map,
                                               sim, drones, const)

                my_mlx = graph_visual.get_mlx()
                raw_img = ImageOperations.xmp_to_img(
                    my_mlx, "images/drone2.xpm")
                drone_img_scaler = ImageScaler()
                img = drone_img_scaler.process(my_mlx, raw_img, 0.05)
                my_mlx.mlx.mlx_destroy_image(my_mlx.mlx_ptr, raw_img.img)
                if img is not None:
                    graph_visual.set_drone_image(img)
                graph_visual.generate_header()
                graph_visual.generate_map(valid_map)
                graph_visual.start_mlx()
                graph_visual.clean_mlx()
            else:
                print("Error: There is no valid path to reach from "
                      "start to goal")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
