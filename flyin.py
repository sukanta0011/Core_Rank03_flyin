# import cProfile
from src.parser.map_parser import MapParser
from src.simulator.path_finder import DepthFirstSearch
from src.simulator.simulation_engine import AdvanceSimulator
from src.visualizer.map_visualizer import ConstantParameters, GraphVisualizer
# from src.visualizer.mlx_tools.LetterToImageMapper import LetterToImageMapper
from src.visualizer.mlx_tools.image_operations import (
    ImageScaler, ImageOperations)
# from src.visualizer.mlx_tools.shape_maker import ShapeGenerator
from src.simulator.helpers import (
    format_valid_paths_into_list,
    create_valid_graph,
    sort_map_by_priority,
    get_min_max_coordinates_from_map,
    calculate_window_size,
    )


def main() -> None:
    # Modify the file path for loading different maps
    file_path = "maps/easy/03_basic_capacity.txt"
    map_parser = MapParser()
    map_parser.parse(file_path)
    # map_parser.show_map()
    drone_counts = map_parser.get_drone_num()
    map = map_parser.get_map()
    # print(get_pos_obj(map, "end").name)
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
            # print(w, h, const.y_cent)
            graph_visual = GraphVisualizer(file_path, map, w, h, valid_map,
                                           sim, drones, const)

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
        else:
            print("Error: There is no valid path to reach from start to goal")


if __name__ == "__main__":
    # cProfile.run('main()')
    main()
    # mlx_test()
