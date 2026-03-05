import cProfile
from srcs.parser.MapParser import MapParser
from srcs.simulator.PathFinder import DepthFirstSearch
from srcs.simulator.Simulator import SimpleSimulator
from srcs.visualizer.GraphVisualizer import ConstantParameters, GraphVisualizer
# from srcs.visualizer.mlx_tools.LetterToImageMapper import LetterToImageMapper
from srcs.visualizer.mlx_tools.image_operations import ImageScaler, ImageOperations
# from srcs.visualizer.mlx_tools.shape_maker import ShapeGenerator
from srcs.simulator.helpers import (
    format_valid_paths_into_list,
    create_valid_graph,
    sort_map_by_priority,
    get_min_max_coordinates_from_map,
    calculate_window_size
    )


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
        simple_sim = SimpleSimulator(graph=map, valid_paths=paths,
                                     drones=drones)
        drones = simple_sim.get_drones()
        const = ConstantParameters()
        w, h = calculate_window_size(const,
                                     get_min_max_coordinates_from_map(map))
        print(w, h, const.y_cent)
        graph_visual = GraphVisualizer("flyin", map, w, h, valid_map,
                                       simple_sim, drones, const)

        my_mlx = graph_visual.get_mlx()
        raw_img = ImageOperations.xmp_to_img(my_mlx, "images/drone2.xpm")
        # img = xmp_to_img(graph_visual.get_mlx(), "images/drone1.xpm")
        drone_img_scaler = ImageScaler()
        img = drone_img_scaler.process(my_mlx, raw_img, 0.05)
        my_mlx.mlx.mlx_destroy_image(my_mlx.mlx_ptr, raw_img.img)
        if img is not None:
            graph_visual.set_drone_image(img)
        graph_visual.generate_header()
        graph_visual.generate_map(valid_map)
        graph_visual.start_mlx()
        graph_visual.clean_mlx()


if __name__ == "__main__":
    # cProfile.run('main()')
    main()
    # mlx_test()
