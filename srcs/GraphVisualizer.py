from typing import Tuple, Dict, List
import math
import time
from mlx import Mlx
from webcolors import name_to_hex, name_to_rgb
from srcs.GraphConstructor import Zone
from srcs.Simulator import Simulator, Drone
# from srcs.LetterToImageMaker import TxtToImage


class ImgData:
    """Structure for image data"""
    def __init__(self):
        self.img = None
        self.w = 0
        self.h = 0
        self.data = None
        self.sl = 0  # size line
        self.bpp = 0  # bits per pixel
        self.iformat = 0


class MlxVar:
    def __init__(self) -> None:
        self.mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.screen_w = 0
        self.screen_h = 0
        self.buff_img = ImgData()
        self.static_bg = ImgData()
        self.drone_img = ImgData()
        self.animation_counter = 0
        self.letter_img = ImgData()
        self.letter_map: Dict[str, ImgData] = {}


class ConstantParameters:
    def __init__(self) -> None:
        self.sq_len = 46
        self.mul = 120
        self.x_offset = 500
        self.fractional_move = 0.05


def copy_img_to_buffer(dest: ImgData, src: ImgData, center: Tuple):
    start_x, start_y = center
    for y in range(src.h):
        dest_start = (start_y + y) * dest.sl + (4 * start_x)
        dest_end = dest_start + (4 * src.w)
        src_start = y * src.sl
        src_end = src_start + (src.w * 4)
        dest.data[dest_start:dest_end] = src.data[src_start:src_end]


def crop_img_to_buffer(dest: ImgData, src: ImgData, center: Tuple):
    start_x, start_y = center
    for y in range(dest.h):
        dest_start = y * dest.sl
        dest_end = dest_start + (4 * dest.w)
        src_start = (start_y + y) * src.sl + (4 * start_x)
        src_end = src_start + (4 * dest.w)
        dest.data[dest_start:dest_end] = src.data[src_start:src_end]


def crop_letter(dest: ImgData, src: ImgData,
                center: Tuple, color: 0xFFFFFFFF,
                bg_color: 0x00000000):
    start_x, start_y = center
    for y in range(dest.h):
        for x in range(dest.w):
            pos = (y + start_y) * src.sl + 4 * (x + start_x)
            dst_pos = (y * dest.sl) + (4 * x)
            if src.data[pos + 1] == 0 and src.data[pos + 2] == 0 and src.data[pos + 2] == 0:
                dest.data[dst_pos: dst_pos + 4] = (bg_color).to_bytes(4, "little")
            else:
                dest.data[dst_pos: dst_pos + 4] = (color).to_bytes(4, "little")


def set_pixel(img: ImgData, center: int | Tuple, color: hex = 0xFFFFFFFF):
    if isinstance(center, int):
        # print(f"one position: {center}")
        pos = center
    elif isinstance(center, Tuple):
        if len(center) == 2:
            x, y = center
            # print(f"x:{x}, y: {y}")
            if x < 0 or x > img.w or y < 0 or y > img.h:
                print(f"pixel outside range, x:{x}, y: {y}")
                return
            pos = (y * img.sl) + (x * (img.bpp // 8))
        else:
            print(f"Error: Invalid center format {center}. Allowed (x, y)")
            return
    else:
        print(f"Error: Invalid center instance {center}. "
              "Allowed instances are int/Tuple")
        return

    try:
        if img.data is not None:
            img.data[pos: pos + 4] = (color).to_bytes(4, 'little')
    except Exception as e:
        # pass
        print(f"Error: {e}")


def draw_circle(mlx_var: MlxVar, center: Tuple, radius: int):
    x, y = center
    for i in range(x - radius, x + radius):
        for j in range(y - radius, y + radius):
            curr_len = math.sqrt((i - x)**2 + (j - y)**2)
            if radius - 1 <= curr_len <= radius + 1:
                mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
                                          mlx_var.win_ptr, i, j, 0xFFFFFFFF)


def draw_line(mlx_var: MlxVar, coordinate: Tuple,
              len: int, direction: str = "v",
              color: hex = 0xFFFFFFFF) -> None:
    x, y = coordinate
    if direction == "h":
        for i in range(x, x + len):
            set_pixel(mlx_var.static_bg, (i, y), color)
            # mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
            #                           mlx_var.win_ptr, i, y, color)
    elif direction == "v":
        for i in range(y, y + len):
            set_pixel(mlx_var.static_bg, (x, i), color)
            # mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
            #                           mlx_var.win_ptr, x, i, color)
    else:
        print(f"Unknown direction: {direction}. "
              "Allowed directions are 'v' and 'h'")


def draw_square(mlx_var: MlxVar, center: Tuple,
                len: int, color: hex = 0xFFFFFFFF):
    x, y = center
    draw_line(mlx_var, (x - len // 2, y + len // 2), len, "h", color)
    draw_line(mlx_var, (x - len // 2, y - len // 2), len, "h", color)
    draw_line(mlx_var, (x + len // 2, y - len // 2), len, "v", color)
    draw_line(mlx_var, (x - len // 2, y - len // 2), len, "v", color)


def draw_rectangle(mlx_var: MlxVar, center: Tuple,
                   h: int, w: int, color: hex = 0xFFFFFFFF):
    x, y = center
    for i in range(y, y + h):
        draw_line(mlx_var, (x, i), h, "h", color)


def connect_two_square(
        mlx_var: MlxVar, cen1: Tuple,
        cen2: Tuple, len: int, color: hex = 0xFFFFFFFF):
    if cen1[0] > cen2[0]:
        x_max, x_min = cen1[0], cen2[0]
    else:
        x_max, x_min = cen2[0], cen1[0]
    if cen1[1] > cen2[1]:
        y_max, y_min = cen1[1], cen2[1]
    else:
        y_max, y_min = cen2[1], cen1[1]

    if x_max - x_min == 0:
        draw_line(mlx_var, (x_min, y_min + len // 2),
                  y_max - y_min - len, "v", color)
    elif y_max - y_min == 0:
        draw_line(mlx_var, (x_min + len // 2, y_min),
                  x_max - x_min - len, "h", color)
    else:
        slope = (cen2[1] - cen1[1]) / (cen2[0] - cen1[0])
        if slope > 0:
            x_min = x_min + len // 2
            y_min = y_min + len // 2
            x_max = x_max - len // 2
            y_max = y_max - len // 2
            slope = (y_max - y_min) / (x_max - x_min)
        else:
            x_min = x_min + len // 2
            y_min = y_min + len // 2
            x_max = x_max - len // 2
            y_max = y_max - len // 2
            slope = - (y_max - y_min) / (x_max - x_min)
        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                if (i - x_min) != 0:
                    if slope < 0:
                        curr_slope = (j - y_max) / (i - x_min)
                    else:
                        curr_slope = (j - y_min) / (i - x_min)
                    if slope - 0.01 <= curr_slope <= slope + 0.01:
                        if abs(curr_slope) != 1:
                            draw_rectangle(mlx_var, (i, j), 1, 1, color)
                        else:
                            draw_rectangle(mlx_var, (i, j), 1, 1, color)


def generate_blank_image(mlx: MlxVar, w: int, h: int) -> ImgData:
    if w <= 0 or h <= 0:
        print("Error: Blank image generation failed"
              f"Wrong w and h has to be positive ({w}, {h})")
        return None
    new_img = ImgData()
    new_img.h = int(h)
    new_img.w = int(w)
    new_img.img = mlx.mlx.mlx_new_image(mlx.mlx_ptr, new_img.w, new_img.h)
    new_img.data, new_img.bpp, new_img.sl, new_img.iformat = \
        mlx.mlx.mlx_get_data_addr(new_img.img)
    return new_img


def xmp_to_img(mlx: MlxVar, image_loc: str) -> ImgData:
    try:
        img = ImgData()
        result = mlx.mlx.mlx_xpm_file_to_image(mlx.mlx_ptr, image_loc)
        img.img, img.w, img.h = result
        img.data, img.bpp, img.sl, img.iformat = \
            mlx.mlx.mlx_get_data_addr(img.img)
        return img
    except Exception as e:
        print(f"Error: Unable to open image, {e}")
        return None


class MyMLX:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.mlx = MlxVar()
        self.init_mlx()

    def init_mlx(self):
        self.mlx.mlx = Mlx()
        self.mlx.mlx_ptr = self.mlx.mlx.mlx_init()
        self.mlx.win_ptr = self.mlx.mlx.mlx_new_window(
            self.mlx.mlx_ptr, self.w, self.h, "Fly IN")
        self.mlx.buff_img = generate_blank_image(self.mlx, self.w, self.h)
        self.mlx.static_bg = generate_blank_image(self.mlx, self.w, self.h)
        self.set_background(self.mlx.static_bg)
        # print(f"Buffer image: {self.mlx.mlx.mlx_get_data_addr(self.mlx.buff_img.img)}")
        self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        self.mlx.mlx.mlx_mouse_hook(self.mlx.win_ptr, self.mymouse, self.mlx)
        self.mlx.mlx.mlx_key_hook(self.mlx.win_ptr, self.mykey, self.mlx)
        self.mlx.mlx.mlx_hook(self.mlx.win_ptr, 33, 0,
                              self.gere_close, self.mlx)

    def get_mlx(self) -> MlxVar:
        return self.mlx

    def start_mlx(self):
        self.mlx.mlx.mlx_loop(self.mlx.mlx_ptr)

    def stop_mlx(self):
        self.mlx.mlx.mlx_loop_exit(self.mlx.mlx_ptr)

    def mymouse(self, button, x, y, mystuff):
        print(f"Got mouse event! button {button} at {x},{y}.")

    def mykey(self, keynum, mlx_var):
        pass
        # print(f"Got key {keynum}, and got my stuff back:")
        # if keynum == 112:
        #     print("Next Move")

    def gere_close(self, mlx_var):
        mlx_var.mlx.mlx_loop_exit(mlx_var.mlx_ptr)

    def put_buffer_image(self):
        if self.mlx.buff_img is not None:
            self.mlx.mlx.mlx_put_image_to_window(
                self.mlx.mlx_ptr, self.mlx.win_ptr, self.mlx.buff_img.img,
                0, 0)
        else:
            print("Error: buffer image is not set")

    def set_background(self, img: ImgData, color: hex = 0xFF000000):
        pixel_bytes = color.to_bytes(4, 'little')
        img.data[:] = pixel_bytes * (img.h * img.w)
        # for i in range(0, img.h * img.w * 4, 4):
        #     set_pixel(img, i, color)

    def rgb_to_hex(self, r: int = 0, g: int = 0, b: int = 0):
        return 0xFF000000 | r << 16 | g << 8 | b

    def color_name_to_code(self, color_name) -> str:
        try:
            color_code = name_to_hex(color_name)
            if "#000000" not in color_code:
                return color_code
            else:
                return "#ffffff"
        except ValueError:
            return "#ffffff"


from srcs.LetterToImageMaker import TxtToImage

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
        self.start_animation()

    def mykey(self, keynum, mlx_var):
        # super().mykey(keynum, mlx_var)
        if keynum == 65293:
            self.update_map(mlx_var)

    def add_txt_to_img_mapper(self, txt_to_img: TxtToImage):
        self.txt_to_img = txt_to_img

    def start_animation(self):
        self.mlx.mlx.mlx_loop_hook(self.mlx.mlx_ptr,
                                   drone_animation_translation,
                                   (self.mlx, self.const,
                                    self.drones, self.graph,
                                    self.print_move, self.print_txt))

    def fill_zone_wih_drones(self, mlx_var: MlxVar, offset: int,
                             center: Tuple, len: int, num: int = 0) -> None:
        x, y = center
        yp = yn = y
        for i in range(num):
            if i % 2 == 0:
                # self.put_image(x, yp, offset)
                copy_img_to_buffer(self.mlx.buff_img, self.mlx.drone_img, (x, yp))
                yp += len
            else:
                yn -= len
                copy_img_to_buffer(self.mlx.buff_img, self.mlx.drone_img, (x, yn))
                # self.put_image(x, yn, offset)

    def remove_drones(self, mlx_var: MlxVar, offset: int,
                      center: Tuple, len: int, num: int = 0) -> None:
        x, y = center
        yp = yn = y
        for i in range(num):
            if i % 2 == 0:
                draw_rectangle(mlx_var, (x - offset, yp - offset),
                               25, 32, 0xFF000000)
                yp += len
            else:
                yn -= len
                draw_rectangle(mlx_var, (x - offset, yn - offset),
                               25, 30, 0xFF000000)

    def draw_all_zones(self, mlx_var: MlxVar, center: Tuple, len: int,
                       name: str, color: hex = 0xFFFFFFFF,
                       num: int = 1) -> None:
        x, y = center
        yp = yn = y
        for i in range(num):
            if i % 2 == 0:
                draw_square(mlx_var, (x, yp), len, color)
                yp += len
            else:
                yn -= len
                draw_square(mlx_var, (x, yn), len, color)
        if y > self.h // 2:
            mlx_var.mlx.mlx_string_put(
                mlx_var.mlx_ptr, mlx_var.win_ptr,
                x, yp, 255, f"{name}")
        else:
            mlx_var.mlx.mlx_string_put(
                mlx_var.mlx_ptr, mlx_var.win_ptr,
                x, yn - len - len // 2, 255, f"{name}")

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
        draw_line(self.mlx, (30, 60), 30, "h", self.rgb_to_hex(g=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "priority",
            (70, 50), factor=0.5)
        draw_line(self.mlx, (30, 90), 30, "h", self.rgb_to_hex(b=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "restricted",
            (70, 80), factor=0.5)
        draw_line(self.mlx, (30, 120), 30, "h")
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "Normal",
            (70, 110), factor=0.5)
        draw_line(self.mlx, (30, 150), 30, "h",  self.rgb_to_hex(r=255))
        self.txt_to_img.print_txt(
            self.mlx, self.mlx.static_bg, "Blocked",
            (70, 140), factor=0.5)
        draw_line(self.mlx, (0, 200), self.mlx.buff_img.w, "h", 0xff2ebdca)

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
            draw_square(self.mlx, (xi, yi), self.const.sq_len, color)
            # self.fill_zone_wih_drones(self.mlx, scale_params.sq_len // 2, (xi + 3, yi + 10),
            #                           scale_params.sq_len, zone.occupancy)
            self.print_txt(self.mlx, self.mlx.static_bg,
                           (xi, yi + int(self.const.sq_len * 2 / 3)), zone.name, "_", 0.3)
            # self.print_capacity(self.mlx, self.mlx.static_bg,
            #                (xi, yi), f"{zone.capacity}:{zone.occupancy}")
            # self.txt_to_img.print_txt(
            #     self.mlx, self.mlx.static_bg, zone.name, (xi, yi))
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
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf),
                            self.const.sq_len, self.rgb_to_hex(g=255))
                    elif link.target.zone_type.value == "restricted":
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), self.const.sq_len,
                            self.rgb_to_hex(b=255))
                    else:
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), self.const.sq_len)
                else:
                    connect_two_square(
                        self.mlx, (xi, yi), (xf, yf), self.const.sq_len,
                        self.rgb_to_hex(r=255))
        copy_img_to_buffer(self.mlx.buff_img, self.mlx.static_bg, (0, 0))
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


def drone_animation_translation(
        params: Tuple[MlxVar, ConstantParameters, 
                      List[Drone], Dict[str, Zone]]):
    mlx_var, const, drones, zones, func_move, func_txt = params
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    mlx_var.buff_img.data[:] = mlx_var.static_bg.data[:]

    all_drone_moved = True
    drone_info = ""
    time.sleep(0.01)
    for drone in drones:
        xf, yf = drone.target_pos
        xi, yi = drone.last_pos
        xc, yc = drone.current_pos
        distance = math.sqrt((yf - yc)**2 + (xf - xc)**2)
        # print(xi, yi, xf, yf, xc, yc, xc >= xf, yc >= yf)
        if distance > 0.05:
            all_drone_moved = False
            if xf - xi == 0:
                # print("Vertical")
                yc += (yf - yi) * const.fractional_move
            elif yf - yi == 0:
                # print("horizontal")
                xc += (xf - xi) * const.fractional_move
            else:
                slope = (yf - yi) / (xf - xi)
                xc += (xf - xi) * const.fractional_move
                # print(f"Angle: {slope}")
                yc = slope * (xc - xi) + yi
        else:
            xc, yc = float(xf), float(yf)
        if len(drone.txt) > 0:
            drone_info += f"{drone.txt} "
        drone.current_pos = [xc, yc]
        xc_scaled = int(xc * const.mul + const.x_offset)
        yc_scaled = int(yc * const.mul + mlx_var.buff_img.h // 2)

        copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img,
                           (xc_scaled - mlx_var.drone_img.w // 2,
                            yc_scaled - mlx_var.drone_img.h // 2))
        func_txt(mlx_var, mlx_var.buff_img, (xc_scaled - mlx_var.drone_img.w // 2,
             yc_scaled - mlx_var.drone_img.h), drone.name, " ", 0.3)
    func_move(mlx_var, mlx_var.buff_img, (50, 210), "", "_",
              0.5, 0xFF00FF00)
    if len(drone_info) > 0:
        func_txt(mlx_var, mlx_var.buff_img, (50, 250), drone_info, " ", 0.4)
    for _, zone in zones.items():
        coord = zone.coordinates
        xi = coord[0] * const.mul + const.x_offset
        yi = coord[1] * const.mul + mlx_var.buff_img.h // 2
        func_txt(mlx_var, mlx_var.buff_img,
                 (xi - 40, yi - 45), f"{zone.capacity}:{zone.occupancy}", " ", 0.4)
    # print([drone.name for drone in drones])
    # copy_img_to_buffer(mlx_var.buff_img, mlx_var.static_bg, (0, 0))
    # print(f"Animation updated: {[(drone.name, drone.target_pos)for drone in drones]}")
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)
    if all_drone_moved:
        pass



def drone_animation_hovering(params: Tuple[MlxVar, str]):
    mlx_var = params[0]
    print(f"test: {params[1]}")
    mlx_var.animation_counter += 1
    time.sleep(0.1)
    y = 100 + int(math.sin(mlx_var.animation_counter) * 4)
    # mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    set_buffer_image_background(mlx_var.buff_img, 400, 600)
    copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img, (100, y))
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)


def set_background(img: ImgData, h: int,
                   w: int, color: hex = 0xFF000000):
    pixel_bytes = color.to_bytes(4, 'little')
    img.data[:] = pixel_bytes * (img.h * img.w)


def mlx_test():
    mlx_var = MyMLX(800, 600)
    draw_line(mlx_var.mlx, (5, 5), 600, "h", 0x0000FFFF)
    draw_square(mlx_var.mlx, (200, 150), 20)
    draw_square(mlx_var.mlx, (250, 300), 20)
    connect_two_square(mlx_var.mlx, (200, 150), (250, 300), 20)
    draw_square(mlx_var.mlx, (250, 150), 20)
    draw_square(mlx_var.mlx, (450, 300), 20)
    connect_two_square(mlx_var.mlx, (250, 150), (450, 300), 20)

    result = mlx_var.mlx.mlx.mlx_xpm_file_to_image(mlx_var.mlx.mlx_ptr, "images/drone1.xpm")
    mlx_var.mlx.drone_img.img, mlx_var.mlx.drone_img.w, mlx_var.mlx.drone_img.h = result
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
