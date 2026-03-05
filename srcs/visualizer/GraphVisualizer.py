from typing import Tuple, Dict, List
import sys
from dataclasses import dataclass
from mlx import Mlx
from srcs.parser.GraphConstructor import Zone
from srcs.simulator.Simulator import Simulator, Drone
from .mlx_tools.base_mlx import MyMLX, MlxVar
from .mlx_tools.image_operations import (
    TxtToImage, ImageScaler, TxtColorChanger, ImgData, ImageOperations)
from .mlx_tools.letter_to_img_map import LetterToImageMapper
from .mlx_tools.shape_maker import ShapeGenerator
from .DroneAnimation import drone_animation_translation


# class GraphicsMlxVar(MlxVar):
#     def __init__(self) -> None:
#         super().__init__()
#         self.buff_img = ImgData()
#         self.static_bg = ImgData()
#         self.drone_img = ImgData()
#         self.letter_img = ImgData()
#         self.letter_map: Dict[str, ImgData] = {}

class ConstantParameters:
    def __init__(self) -> None:
        self.sq_len = 50
        self.mul = 150
        self.x_offset = 500
        self.y_offset = 200
        self.y_cent = 200
        self.fractional_move = 0.05
        self.win_w = 800
        self.win_h = 400
        self.header_bg = 0xff2ebdca


@dataclass
class KeyMap:
    """Data class to to store multiple keys for a specific action"""
    MOVE: Tuple[int, int] = (49, 65436)       # Key '1' and Numpad '1'
    # TOGGLE_PATH: Tuple[int, int] = (50, 65433)  # Key '2' and Numpad '2'
    # COLOR: Tuple[int, int] = (51, 65435)       # Key '3' and Numpad '3'
    QUIT: Tuple[int, int] = (52, 65430)        # Key '4' and Numpad '4'


class GraphVisualizer(MyMLX):
    def __init__(self, name: str, graph: Dict[str, Zone], w: int, h: int,
                 valid_paths: Dict[str, List], simulator: Simulator,
                 drones: List[Drone], const: ConstantParameters):
        super().__init__(name, w, h)
        self.graph = graph
        self.drones = drones
        self.valid_paths = valid_paths
        self.simulator = simulator
        self.const = const
        self.counter = 0
        self.move_txt = "Move: 0"
        self.throughput = []
        self.init_letter_map()
        self.start_animation()

    def init_letter_map(self) -> None:
        """Initializes the font system and configures the text processing
          pipeline.

        Loads the alphabet sprite sheet and adds scaling and coloring stages
        to the text rendering engine.
        """
        self.txt_to_image = None
        try:
            letter_to_img_map = LetterToImageMapper(self.mlx)
            letter_to_img_map.create_map()

            self.txt_to_image = TxtToImage(
                self.mlx.base_letter_map,
                self.mlx.extended_letter_map)
            self.txt_to_image.add_stages(ImageScaler())
            self.txt_to_image.add_stages(TxtColorChanger())
        except Exception as e:
            print("Following Error encounter during creation of"
                  f"letter map: {e}", file=sys.stderr)

    def mykey(self, keynum, mlx_var):
        # super().mykey(keynum, mlx_var)
        if keynum in KeyMap.MOVE:
            self.update_map(mlx_var)
        if keynum in KeyMap.QUIT:
            self.stop_mlx(self.mlx)

    # def stop_mlx(self):
    #     self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, self.mlx.drone_img.img)
    #     self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, self.mlx.letter_img.img)
    #     for _, img in self.mlx.letter_map.items():
    #         self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, img.img)
    #     return super().stop_mlx()

    def start_animation(self):
        self.mlx.mlx.mlx_loop_hook(self.mlx.mlx_ptr,
                                   drone_animation_translation,
                                   (self.mlx, self.const,
                                    self.drones, self.graph,
                                    self.print_move, self.print_txt,
                                    self.print_throughput))

    def print_txt(self, mlx_var: MlxVar, img: ImgData,
                  center: Tuple, name: str, split_by: str,
                  factor: float, font_clr=0xffffffff, bg_clr=0x00000000):
        x, y = center
        split_names = name.split(split_by)
        for name in split_names:
            self.txt_to_image.print_txt(
                self.mlx, img, name, (x, y), factor,
                font_clr, bg_clr)
            y += int(50 * factor)

    def print_move(self, mlx_var: MlxVar, img: ImgData,
                   center: Tuple, name: str, split_by: str,
                   factor: float, font_clr=0xffffffff, bg_clr=0x00000000):
        x, y = center
        split_names = self.move_txt.split('\n')
        for name in split_names:
            self.txt_to_image.print_txt(
                self.mlx, img, name, (x, y), factor,
                font_clr, bg_clr)
            y += int(50 * factor)
    
    def print_throughput(self, mlx_var: MlxVar, img: ImgData,
                   center: Tuple, name: str, split_by: str,
                   factor: float, font_clr=0xffffffff, bg_clr=0x00000000):
        x, y = center
        for info in self.throughput:
            self.txt_to_image.print_txt(
                self.mlx, img, f"{info[0]}: {info[1]}", (x, y), factor,
                font_clr, bg_clr)
            y += int(50 * factor)
        

    def set_drone_image(self, img: ImgData) -> None:
        self.mlx.drone_img = img

    def print_link_capacity(self, cord1: Tuple[int, int],
                            cord2: Tuple[int, int], capacity: int):
        xi, xf = cord1
        yi, yf = cord2
        extra_gap = 4
        if yf == yi:
            x_txt = (xf + xi) // 2
            y_txt = yf + extra_gap
        elif xf == xi:
            x_txt = xf + extra_gap
            y_txt = (yf + yi) // 2
        else:
            x_txt = (xf + xi) // 2
            y_txt = (yf + yi) // 2

        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, str(capacity), (x_txt, y_txt), 0.5)

    def generate_header(self):
        self.set_background(self.mlx.static_bg, (0, 0),
                            self.const.win_w,
                            self.const.y_offset, self.const.header_bg)
        # self.set_background(self.mlx.static_bg, (0, self.const.y_offset),
        #                     self.const.x_offset, self.const.win_h - self.const.y_offset,
        #                     0xff2ebdca)

        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "Welcome to FLYIN",
            (10, 10), font_color=0xFF000000, bg_color=self.const.header_bg)
        ShapeGenerator.draw_line(self.mlx, self.mlx.static_bg, (30, 60), 30,
                                 "h", self.rgb_to_hex(g=255), 3)
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "priority",
            (70, 50), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)
        ShapeGenerator.draw_line(self.mlx, self.mlx.static_bg, (30, 90), 30,
                                 "h", self.rgb_to_hex(b=255), 3)
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "restricted",
            (70, 80), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)
        ShapeGenerator.draw_line(self.mlx, self.mlx.static_bg, (30, 120), 30, "h", thickness=3)
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "Normal",
            (70, 110), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)
        ShapeGenerator.draw_line(self.mlx, self.mlx.static_bg, (30, 150), 30, "h",  self.rgb_to_hex(r=255), 3)
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "Blocked",
            (70, 140), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)
        # self.generate_shape.draw_line(self.mlx.static_bg, (0, 200), self.mlx.buff_img.w, "h", 0xff2ebdca)

        # Key info:
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "1: Move",
            (200, 50), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)
        self.txt_to_image.print_txt(
            self.mlx, self.mlx.static_bg, "4: Quit",
            (200, 80), factor=0.5, font_color=0xFF000000, bg_color=self.const.header_bg)

    def generate_map(self, valid_paths: Dict[str, List]):
        for key, zone in self.graph.items():
            coord = zone.coordinates
            color = 0xFFFFFFFF
            xi = coord[0] * self.const.mul + self.const.x_offset
            yi = coord[1] * self.const.mul + self.const.y_cent
            # print(f"Coords: {coord}, {xi}, {yi}")
            if zone.color is not None:
                hex_str = self.color_name_to_code(zone.color)
                color = 0xFF000000 | int(hex_str[1:], 16)
            # self.draw_all_zones(self.mlx, (xi, yi), self.const.sq_len,
            #                     zone.name, color, zone.capacity)
            ShapeGenerator.draw_hollow_square(self.mlx, self.mlx.static_bg,
                                              (xi, yi),
                                              self.const.sq_len, color)
            # self.fill_zone_wih_drones(self.mlx, scale_params.sq_len // 2, (xi + 3, yi + 10),
            #                           scale_params.sq_len, zone.occupancy)
            self.print_txt(self.mlx, self.mlx.static_bg,
                           (xi, yi + int(self.const.sq_len * 2 / 3)),
                           zone.name, "_", 0.3)
            valid_links = valid_paths[key]
            # print(zone.name, xi, yi, self.h // 2)
            for link in zone.links:
                coord = link.target.coordinates
                xf = coord[0] * self.const.mul + self.const.x_offset
                yf = coord[1] * self.const.mul + self.const.y_cent
                # print(zone.name, link.target.name, xi, xf, yi, yf)
                self.print_link_capacity((xi, xf), (yi, yf), link.capacity)
                if link.target.name in valid_links:
                    if link.target.zone_type.value == "priority":
                        ShapeGenerator.connect_two_square(self.mlx,
                            self.mlx.static_bg, (xi, yi), (xf, yf),
                            self.const.sq_len, self.rgb_to_hex(g=255))
                    elif link.target.zone_type.value == "restricted":
                        ShapeGenerator.connect_two_square(self.mlx,
                            self.mlx.static_bg, (xi, yi), (xf, yf),
                            self.const.sq_len,
                            self.rgb_to_hex(b=255))
                    else:
                        ShapeGenerator.connect_two_square(self.mlx,
                            self.mlx.static_bg, (xi, yi), (xf, yf),
                            self.const.sq_len)
                else:
                    ShapeGenerator.connect_two_square(self.mlx,
                        self.mlx.static_bg, (xi, yi), (xf, yf),
                        self.const.sq_len,
                        self.rgb_to_hex(r=255))
        ImageOperations.copy_img(self.mlx.buff_img, self.mlx.static_bg, (0, 0))
        self.put_buffer_image()

    def update_map(self, simulator: Simulator):
        # self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)\
        drones_moving = [drone.moving for drone in self.drones]
        if True not in drones_moving:
            drone_movement = self.simulator.next_move(self.valid_paths)
            if len(drone_movement) == 0:
                print("All drones reached to the goal")
                self.move_txt = f"Move: {self.counter}\nCongratulation."\
                                "\nSimulation completed."
            else:
                # print(drone_movement)
                drone_moved = drone_movement.split(" ")
                self.counter += 1
                self.move_txt = f"Move: {self.counter}"
                print(f"Move no: {self.counter}, Drones Moved: {len(drone_moved) - 1}")
                self.throughput.append((self.counter, len(drone_moved) - 1))
                for drone in self.drones:
                    print(f"{drone.name}: {drone.total_moves}")
                # self.print_txt(self.mlx, self.mlx.buff_img,
                #                (100, 100), drone_movement, " ", 0.4)
            # self.generate_map(self.valid_paths)
        else:
            print("Drones are moving, please wait.")


def mlx_test():
    mlx_var = MyMLX('flyin', 800, 600)
    ShapeGenerator.draw_line(mlx_var.mlx, mlx_var.mlx.static_bg, (5, 5), 600, "h", 0x0000FFFF)
    ShapeGenerator.draw_hollow_square(mlx_var.mlx, mlx_var.mlx.static_bg, (200, 150), 20)
    ShapeGenerator.draw_hollow_square(mlx_var.mlx, mlx_var.mlx.static_bg, (250, 300), 20)
    ShapeGenerator.connect_two_square(mlx_var.mlx, mlx_var.mlx.static_bg, (200, 150), (250, 300), 20)
    ShapeGenerator.draw_hollow_square(mlx_var.mlx, mlx_var.mlx.static_bg, (250, 150), 20)
    ShapeGenerator.draw_hollow_square(mlx_var.mlx, mlx_var.mlx.static_bg, (450, 300), 20)
    ShapeGenerator.connect_two_square(mlx_var.mlx, mlx_var.mlx.static_bg, (250, 150), (450, 300), 20)

    result = mlx_var.mlx.mlx.mlx_xpm_file_to_image(mlx_var.mlx.mlx_ptr,
                                                   "images/drone1.xpm")
    mlx_var.mlx.drone_img.img, mlx_var.mlx.drone_img.w,\
        mlx_var.mlx.drone_img.h = result
    mlx_var.mlx.drone_img.data, mlx_var.mlx.drone_img.bpp, \
        mlx_var.mlx.drone_img.sl, mlx_var.mlx.drone_img.iformat = \
        mlx_var.mlx.mlx.mlx_get_data_addr(mlx_var.mlx.drone_img.img)
    print(mlx_var.mlx.drone_img.w, mlx_var.mlx.drone_img.h)
    # copy_img_to_buffer(mlx_var.static_bg, mlx_var.drone_img, (100, 100))
    # set_buffer_image_background(mlx_var.buff_img, 400, 600, 0xFF00FFFF)
    # copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img, (100, 200))

    # draw_square(mlx_var, (100, 200), 40)
    # draw_square(mlx_var, (300, 100), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 100), 40)
    # draw_square(mlx_var, (300, 300), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 300), 40)
    # draw_square(mlx_var, (400, 200), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 100), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 300), 40)
    zone1 = Zone("zone1", 0, 0)
    zone2 = Zone("zone2", 1, 0)
    zone3 = Zone("zone3", 2, -1)
    drone1 = Drone(0, zone1)
    drone1.target_pos = list(zone2.coordinates)
    drone2 = Drone(1, zone2)
    drone2.target_pos = list(zone3.coordinates)
    # drone2.current_coords = [1, 0]

    scale = ConstantParameters()

    # mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
    #                                     mlx_var.buff_img.img, 0, 0)
    mlx_var.mlx.mlx.mlx_loop_hook(mlx_var.mlx.mlx_ptr,
                              drone_animation_translation,
                              (mlx_var.mlx, scale, [drone1, drone2], {}, ))
    mlx_var.start_mlx()


if __name__ == "__main__":
    mlx_test()
