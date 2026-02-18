from typing import Tuple, Dict, List
from mlx import Mlx
from srcs.mlx_tools.BaseMLX import MyMLX, MlxVar, ImgData
from srcs.parser.GraphConstructor import Zone
from srcs.simulator.Simulator import Simulator, Drone
from srcs.mlx_tools.ImageOperations import TxtToImage, copy_img, xmp_to_img
from srcs.mlx_tools.ShapeMaker import ShapeGenerator
from srcs.visualizer.DroneAnimation import drone_animation_translation


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
        self.sq_len = 46
        self.mul = 120
        self.x_offset = 500
        self.fractional_move = 0.05


class GraphVisualizer(MyMLX):
    def __init__(self, graph: Dict[str, Zone], w: int, h: int,
                 valid_paths: Dict[str, List], simulator: Simulator,
                 drones: List[Drone]):
        super().__init__(w, h)
        self.graph = graph
        self.drones = drones
        self.valid_paths = valid_paths
        self.simulator = simulator
        self.const = ConstantParameters()
        self.counter = 0
        self.move_txt = "Move: 0"
        self.generate_shape = ShapeGenerator(self.mlx)
        self.start_animation()

    def mykey(self, keynum, mlx_var):
        # super().mykey(keynum, mlx_var)
        if keynum == 65293:
            self.update_map(mlx_var)

    def stop_mlx(self):
        self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, self.mlx.drone_img.img)
        self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, self.mlx.letter_img.img)
        for _, img in self.mlx.letter_map.items():
            self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, img.img)
        return super().stop_mlx()

    def add_txt_to_img_mapper(self, txt_to_img: TxtToImage):
        self.txt_to_img = txt_to_img

    def start_animation(self):
        self.mlx.mlx.mlx_loop_hook(self.mlx.mlx_ptr,
                                   drone_animation_translation,
                                   (self.mlx, self.const,
                                    self.drones, self.graph,
                                    self.print_move, self.print_txt))

    def print_txt(self, mlx_var: MlxVar, img: ImgData,
                  center: Tuple, name: str, split_by: str,
                  factor: float, font_clr=0xffffffff, bg_clr=0x00000000):
        x, y = center
        split_names = name.split(split_by)
        for name in split_names:
            self.txt_to_img.print_txt(
                self.mlx, img, name, (x, y), factor,
                font_clr, bg_clr)
            y += int(50 * factor)

    def print_move(self, mlx_var: MlxVar, img: ImgData,
                   center: Tuple, name: str, split_by: str,
                   factor: float, font_clr=0xffffffff, bg_clr=0x00000000):
        x, y = center
        split_names = self.move_txt.split('\n')
        for name in split_names:
            self.txt_to_img.print_txt(
                self.mlx, img, name, (x, y), factor,
                font_clr, bg_clr)
            y += int(50 * factor)

    def set_drone_image(self, img: ImgData) -> None:
        self.mlx.drone_img = img

    def print_link_capacity(self, cord1: Tuple[int, int],
                            cord2: Tuple[int, int], capacity: int):
        xi, xf = cord1
        yi, yf = cord2
        if yf == yi:
            x_txt = (xf + xi) // 2
            y_txt = yf
        elif xf == xi:
            x_txt = xf
            y_txt = (yf + yi) // 2
        else:
            x_txt = (xf + xi) // 2
            y_txt = (yf + yi) // 2

        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, str(capacity), (x_txt, y_txt), 0.5)

    def generate_header(self):
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "Welcome to FLYIN",
            (10, 10), font_color=0xFFFF0000)
        self.generate_shape.draw_line(self.mlx.static_bg, (30, 60), 30, "h", self.rgb_to_hex(g=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "priority",
            (70, 50), factor=0.5)
        self.generate_shape.draw_line(self.mlx.static_bg, (30, 90), 30, "h", self.rgb_to_hex(b=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "restricted",
            (70, 80), factor=0.5)
        self.generate_shape.draw_line(self.mlx.static_bg, (30, 120), 30, "h")
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "Normal",
            (70, 110), factor=0.5)
        self.generate_shape.draw_line(self.mlx.static_bg, (30, 150), 30, "h",  self.rgb_to_hex(r=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "Blocked",
            (70, 140), factor=0.5)
        self.generate_shape.draw_line(self.mlx.static_bg, (0, 200), self.mlx.buff_img.w, "h", 0xff2ebdca)

    def generate_map(self, valid_paths: Dict[str, List]):
        for key, zone in self.graph.items():
            coord = zone.coordinates
            color = 0xFFFFFFFF
            xi = coord[0] * self.const.mul + self.const.x_offset
            yi = coord[1] * self.const.mul + self.h // 2
            # print(f"Coords: {coord}, {xi}, {yi}")
            if zone.color is not None:
                hex_str = self.color_name_to_code(zone.color)
                color = 0xFF000000 | int(hex_str[1:], 16)
            # self.draw_all_zones(self.mlx, (xi, yi), self.const.sq_len,
            #                     zone.name, color, zone.capacity)
            self.generate_shape.draw_square(self.mlx.static_bg, (xi, yi), self.const.sq_len, color)
            # self.fill_zone_wih_drones(self.mlx, scale_params.sq_len // 2, (xi + 3, yi + 10),
            #                           scale_params.sq_len, zone.occupancy)
            self.print_txt(self.mlx, self.mlx.static_bg,
                           (xi, yi + int(self.const.sq_len * 2 / 3)), zone.name, "_", 0.3)
            valid_links = valid_paths[key]
            # print(zone.name, xi, yi, self.h // 2)
            for link in zone.links:
                coord = link.target.coordinates
                xf = coord[0] * self.const.mul + self.const.x_offset
                yf = coord[1] * self.const.mul + self.h // 2
                # print(zone.name, link.target.name, xi, xf, yi, yf)
                self.print_link_capacity((xi, xf), (yi, yf), link.capacity)
                if link.target.name in valid_links:
                    if link.target.zone_type.value == "priority":
                        self.generate_shape.connect_two_square(
                            self.mlx.static_bg, (xi, yi), (xf, yf),
                            self.const.sq_len, self.rgb_to_hex(g=255))
                    elif link.target.zone_type.value == "restricted":
                        self.generate_shape.connect_two_square(
                            self.mlx.static_bg, (xi, yi), (xf, yf), self.const.sq_len,
                            self.rgb_to_hex(b=255))
                    else:
                        self.generate_shape.connect_two_square(
                            self.mlx.static_bg, (xi, yi), (xf, yf), self.const.sq_len)
                else:
                    self.generate_shape.connect_two_square(
                        self.mlx.static_bg, (xi, yi), (xf, yf), self.const.sq_len,
                        self.rgb_to_hex(r=255))
        copy_img(self.mlx.buff_img, self.mlx.static_bg, (0, 0))
        self.put_buffer_image()

    def update_map(self, simulator: Simulator):
        # self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        drone_movement = self.simulator.next_move(self.valid_paths)
        if len(drone_movement) == 0:
            print("All drones reached to the goal")
            self.move_txt = f"Move: {self.counter}\nCongratulation."\
                            "\nSimulation completed."     
        else:
            print(drone_movement)
            self.counter += 1
            self.move_txt = f"Move: {self.counter}"
            # self.print_txt(self.mlx, self.mlx.buff_img,
            #                (100, 100), drone_movement, " ", 0.4)
        # self.generate_map(self.valid_paths)


def mlx_test():
    mlx_var = MyMLX(800, 600)
    draw_line(mlx_var.mlx, (5, 5), 600, "h", 0x0000FFFF)
    draw_square(mlx_var.mlx, (200, 150), 20)
    draw_square(mlx_var.mlx, (250, 300), 20)
    connect_two_square(mlx_var.mlx, (200, 150), (250, 300), 20)
    draw_square(mlx_var.mlx, (250, 150), 20)
    draw_square(mlx_var.mlx, (450, 300), 20)
    connect_two_square(mlx_var.mlx, (250, 150), (450, 300), 20)

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
                              (mlx_var.mlx, scale, [drone1, drone2]))
    mlx_var.start_mlx()


if __name__ == "__main__":
    mlx_test()
