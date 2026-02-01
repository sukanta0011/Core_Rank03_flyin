from srcs.MapParser import MapParser
from srcs.PathFinder import DepthFirstSearch
from srcs.Simulator import SimulatorOne


def main():
    file_path = "maps/easy/02_simple_fork.txt"
    # file_path = "maps/medium/01_dead_end_trap.txt"
    # file_path = "maps/medium/02_circular_loop.txt"
    # file_path = "maps/hard/01_maze_nightmare.txt"
    # file_path = "maps/challenger/01_the_impossible_dream.txt"
    # file_path = "maps/invalid/map1.txt"
    map_parser = MapParser()
    map_parser.parse(file_path)
    # map_parser.show_map()
    drones = map_parser.get_drone_num()
    map = map_parser.get_map()
    if map is not None and drones is not None:
        dfs = DepthFirstSearch(map)
        paths = dfs.find_valid_paths()
        sim_one = SimulatorOne(graph=map, valid_paths=paths,
                               drones=drones)
        sim_one.start_simulation()


if __name__ == "__main__":
    main()
