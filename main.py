from srcs.MapParser import MapParser
from srcs.PathFinder import DepthFirstSearch
from srcs.Simulator import SimpleSimulator
from srcs.GraphVisualizer import GraphVisualizer
from srcs.helpers import (
    get_pos_obj,
    format_valid_paths_into_list,
    create_valid_graph,
    sort_map_by_priority
    )
from srcs.GraphVisualizer import mlx_test

def main():
    # file_path = "maps/easy/example_map.txt"
    # file_path = "maps/easy/03_basic_capacity.txt"
    # file_path = "maps/medium/02_circular_loop.txt"
    # file_path = "maps/medium/03_priority_puzzle.txt"
    # file_path = "maps/hard/01_maze_nightmare.txt"
    # file_path = "maps/hard/02_capacity_hell.txt"
    file_path = "maps/hard/03_ultimate_challenge.txt"
    # file_path = "maps/challenger/01_the_impossible_dream.txt"
    # file_path = "maps/invalid/map1.txt"
    # file_path = "maps/challenger/01_the_impossible_dream.txt"
    # file_path = "maps/my_maps/priority_map1.txt"
    map_parser = MapParser()
    map_parser.parse(file_path)
    # map_parser.show_map()
    drones = map_parser.get_drone_num()
    map = map_parser.get_map()
    # print(get_pos_obj(map, "end").name)
    if map is not None and drones is not None:
        dfs = DepthFirstSearch(map)
        paths = dfs.find_valid_paths()
        new_paths = format_valid_paths_into_list(paths)
        hubs_name = list(map.keys())
        valid_map = create_valid_graph(hubs_name, new_paths)
        valid_map = sort_map_by_priority(valid_map, map)
        # for path in paths:
        #     print(path)
        simple_sim = SimpleSimulator(graph=map, valid_paths=paths,
                                     drones=drones)
        # sim_one.start_simulation(valid_map)
        simple_sim.show_zone_state()
        simple_sim.start_simulation(valid_map)
    graph_visual = GraphVisualizer(map, 1600, 900)
    graph_visual.generate_map(valid_map)


if __name__ == "__main__":
    main()
    # mlx_test()
