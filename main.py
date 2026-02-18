from srcs.parser.MapParser import MapParser
from srcs.simulator.PathFinder import DepthFirstSearch
from srcs.simulator.Simulator import SimpleSimulator
from srcs.visualizer.GraphVisualizer import GraphVisualizer
from srcs.mlx_tools.LetterToImageMapper import LetterToImageMapper
from srcs.mlx_tools.ImageOperations import(
    ImageScaler,
    TxtColorChanger,
    TxtToImage, crop_img, xmp_to_img)
from srcs.simulator.helpers import (
    format_valid_paths_into_list,
    create_valid_graph,
    sort_map_by_priority
    )


def main():
    # file_path = "maps/easy/example_map.txt"
    # file_path = "maps/easy/03_basic_capacity.txt"
    # file_path = "maps/medium/02_circular_loop.txt"
    # file_path = "maps/medium/03_priority_puzzle.txt"
    # file_path = "maps/hard/01_maze_nightmare.txt"
    file_path = "maps/hard/02_capacity_hell.txt"
    # file_path = "maps/hard/03_ultimate_challenge.txt"
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
        graph_visual = GraphVisualizer(map, 2400, 800, valid_map,
                                       simple_sim, drones)

        letter_map = LetterToImageMapper(graph_visual.get_mlx())
        letter_map.create_map()
        letter_scaler = ImageScaler()
        letter_color = TxtColorChanger()
        txt_to_img = TxtToImage(graph_visual.get_mlx().letter_map)
        txt_to_img.add_stages(letter_scaler)
        txt_to_img.add_stages(letter_color)

        graph_visual.add_txt_to_img_mapper(txt_to_img)
        my_mlx = graph_visual.get_mlx()
        raw_img = xmp_to_img(my_mlx, "images/drone2.xpm")
        # img = xmp_to_img(graph_visual.get_mlx(), "images/drone1.xpm")
        drone_img_scaler = ImageScaler()
        img = drone_img_scaler.process(my_mlx, raw_img, 0.05)
        my_mlx.mlx.mlx_destroy_image(my_mlx.mlx_ptr, raw_img.img)
        if img is not None:
            graph_visual.set_drone_image(img)
        graph_visual.generate_header()
        graph_visual.generate_map(valid_map)
        graph_visual.start_mlx()


if __name__ == "__main__":
    main()
    # mlx_test()
