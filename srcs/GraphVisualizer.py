from typing import Tuple, Dict, List
import math
import time
from mlx import Mlx
from webcolors import name_to_hex, name_to_rgb
from srcs.GraphConstructor import Zone
from srcs.Simulator import Simulator

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
        self.drone_img = ImgData()
        self.animation_counter = 0

class ShapeGenerator:
    pass


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
            set_pixel(mlx_var.buff_img, (i, y), color)
            # mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
            #                           mlx_var.win_ptr, i, y, color)
    elif direction == "v":
        for i in range(y, y + len):
            set_pixel(mlx_var.buff_img, (x, i), color)
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
                  y_max - y_min - len, "h", color)
    elif y_max - y_min == 0:
        draw_line(mlx_var, (x_min + len // 2, y_min),
                  x_max - x_min - len, "v", color)
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
                    if curr_slope == slope:
                        if abs(curr_slope) != 1:
                            draw_rectangle(mlx_var, (i, j), 4, 4, color)
                        else:
                            draw_rectangle(mlx_var, (i, j), 1, 1, color)


class MyMLX:
    def __init__(self, graph: Dict[str, Zone], w: int, h: int,
                 valid_paths: Dict[str, List], simulator: Simulator):
        self.graph = graph
        self.w = w
        self.h = h
        self.mlx = MlxVar()
        self.valid_paths = valid_paths
        self.simulator = simulator
        self.init_mlx()

    def init_mlx(self):
        self.mlx.mlx = Mlx()
        self.mlx.mlx_ptr = self.mlx.mlx.mlx_init()
        self.mlx.win_ptr = self.mlx.mlx.mlx_new_window(self.mlx.mlx_ptr, self.w, self.h, "Fly IN")
        self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        self.mlx.mlx.mlx_mouse_hook(self.mlx.win_ptr, self.mymouse, self.mlx)
        self.mlx.mlx.mlx_key_hook(self.mlx.win_ptr, self.mykey, self.mlx)
        self.mlx.mlx.mlx_hook(self.mlx.win_ptr, 33, 0, self.gere_close, self.mlx)

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


class GraphVisualizer(MyMLX):
    def mykey(self, keynum, mlx_var):
        # super().mykey(keynum, mlx_var)
        if keynum == 65293:
            self.update_map(mlx_var)

    def put_image(self, xc: int, yc: int, offset: int):
        x = xc - offset
        y = yc - offset
        self.mlx.mlx.mlx_put_image_to_window(
            self.mlx.mlx_ptr, self.mlx.win_ptr, self.mlx.img, x, y)

    def fill_zone_wih_drones(self, mlx_var: MlxVar, offset: int,
                             center: Tuple, len: int, num: int = 0) -> None:
        x, y = center
        yp = yn = y
        for i in range(num):
            if i % 2 == 0:
                self.put_image(x, yp, offset)
                yp += len
            else:
                yn -= len
                self.put_image(x, yn, offset)

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

    def add_xmp_image(self, image_loc: str) -> None:
        try:
            result = self.mlx.mlx.mlx_xpm_file_to_image(
                self.mlx.mlx_ptr, image_loc)
            self.mlx.img, _, _ = result
        except Exception as e:
            print(f"Error: Unable to open image, {e}")

    def print_link_capacity(self, cord1: Tuple[int, int],
                            cord2: Tuple[int, int], capacity: int):
        xi, xf = cord1
        yi, yf = cord2
        if yf == yi:
            x_txt = (xf + xi) // 2
            y_txt = yf
        elif xf == xi:
            x_txt = xf
            y_txt = (self.h + yf - yi) // 2
        elif (yf - yi) / (xf - xi) >= 0:
            x_txt = (xf + xi) // 2
            if yi >= self.h // 2:
                y_txt = (self.h + yf - yi) // 2
            else:
                y_txt = (self.h + yi - yf) // 2
        elif (yf - yi) / (xf - xi) < 0:
            x_txt = (xf + xi) // 2
            if yi <= self.h // 2:
                y_txt = (self.h + yf - yi) // 2
            else:
                y_txt = (self.h - yf + yi) // 2
        self.mlx.mlx.mlx_string_put(
            self.mlx.mlx_ptr, self.mlx.win_ptr, x_txt,
            y_txt, 255, str(capacity))

    def generate_map(self, valid_paths: Dict[str, List]):
        sq_len = 36
        mul = 120
        offset = 100
        for key, zone in self.graph.items():
            coord = zone.coordinates
            color = 0xFFFFFFFF
            xi = coord[0] * mul + offset
            yi = coord[1] * mul + self.h // 2
            if zone.color is not None:
                hex_str = self.color_name_to_code(zone.color)
                color = 0xFF000000 | int(hex_str[1:], 16)
            self.draw_all_zones(self.mlx, (xi, yi), sq_len,
                                zone.name, color, zone.capacity)
            self.fill_zone_wih_drones(self.mlx, sq_len // 2, (xi + 3, yi + 10),
                                      sq_len, zone.occupancy)
            valid_links = valid_paths[key]
            # print(zone.name, xi, yi, self.h // 2)
            for link in zone.links:
                coord = link.target.coordinates
                xf = coord[0] * mul + offset
                yf = coord[1] * mul + self.h // 2
                # print(zone.name, link.target.name, xi, xf, yi, yf)
                self.print_link_capacity((xi, xf), (yi, yf), link.capacity)
                if link.target.name in valid_links:
                    if link.target.zone_type.value == "priority":
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf),
                            sq_len, self.rgb_to_hex(g=255))
                    elif link.target.zone_type.value == "restricted":
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), sq_len,
                            self.rgb_to_hex(b=255))
                    else:
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), sq_len)
                else:
                    connect_two_square(
                        self.mlx, (xi, yi), (xf, yf), sq_len,
                        self.rgb_to_hex(r=255))
        # self.start_mlx()

    def update_map(self, simulator: Simulator):
        # self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        sq_len = 36
        mul = 120
        offset = 100
        for key, zone in self.graph.items():
            coord = zone.coordinates
            xi = coord[0] * mul + offset
            yi = coord[1] * mul + self.h // 2
            self.remove_drones(self.mlx, sq_len // 2, (xi + 3, yi + 10),
                               sq_len, zone.occupancy)
            # self.fill_zone_wih_drones(self.mlx, sq_len // 2, (xi + 3, yi + 10),
            #                           sq_len, zone.occupancy)
        drone_movement = self.simulator.next_move(self.valid_paths)
        if len(drone_movement) == 0:
            print("All drones reached to the goal")
        else:
            print(drone_movement)
        # self.generate_map(self.valid_paths)
        for key, zone in self.graph.items():
            coord = zone.coordinates
            xi = coord[0] * mul + offset
            yi = coord[1] * mul + self.h // 2
            self.fill_zone_wih_drones(self.mlx, sq_len // 2, (xi + 3, yi + 10),
                                      sq_len, zone.occupancy)



def mymouse(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def mykey(keynum, mlx_var):
    pass
    # print(f"Got key {keynum}, and got my stuff back:")
    # if keynum == 112:
    #     print("Next Move")


def gere_close(mlx_var):
    mlx_var.mlx.mlx_loop_exit(mlx_var.mlx_ptr)


def rgbh_to_hex(h: int, r: int = 0, g: int = 0, b: int = 0):
    return 0x00000000 | h << 24 | r << 16 | g << 8 | b


def drone_animation(mlx_var: MlxVar):
    mlx_var.animation_counter += 1
    time.sleep(0.1)
    y = 100 + int(math.sin(mlx_var.animation_counter) * 4)
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    for i in range(600):
        for j in range(400):
            set_pixel(mlx_var.buff_img, (i, j), 0x00000000)
    copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img, (100, y))
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)


def mlx_test():
    mlx_var = MlxVar()
    mlx_var.mlx = Mlx()
    mlx_var.mlx_ptr = mlx_var.mlx.mlx_init()
    mlx_var.win_ptr = mlx_var.mlx.mlx_new_window(mlx_var.mlx_ptr, 600, 400, "win title")
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    # mlx_var.mlx.mlx_string_put(mlx_var.mlx_ptr, mlx_var.win_ptr, 10, 10, 255, "Hello PyMlx!")
    (ret, mlx_var.screen_w, mlx_var.screen_h) = mlx_var.mlx.mlx_get_screen_size(mlx_var.mlx_ptr)
    # print(f"Got screen size: {w} x {h} .")
    mlx_var.buff_img.img = mlx_var.mlx.mlx_new_image(mlx_var.mlx_ptr, 600, 400)
    mlx_var.buff_img.h = 400
    mlx_var.buff_img.w = 600
    mlx_var.buff_img.data, mlx_var.buff_img.bpp, mlx_var.buff_img.sl, mlx_var.buff_img.iformat = \
        mlx_var.mlx.mlx_get_data_addr(mlx_var.buff_img.img)
    print(mlx_var.buff_img.data)
    stuff = [1, 2]
    mlx_var.mlx.mlx_mouse_hook(mlx_var.win_ptr, mymouse, stuff)
    mlx_var.mlx.mlx_key_hook(mlx_var.win_ptr, mykey, mlx_var)
    mlx_var.mlx.mlx_hook(mlx_var.win_ptr, 33, 0, gere_close, mlx_var)
    # draw_colormap(mlx_var)
    draw_line(mlx_var, (5, 5), 600, "h", 0x0000FFFF)
    draw_square(mlx_var, (200, 150), 20)
    draw_square(mlx_var, (250, 300), 20)
    connect_two_square(mlx_var, (200, 150), (250, 300), 20)
    draw_square(mlx_var, (250, 150), 20)
    draw_square(mlx_var, (450, 300), 20)
    connect_two_square(mlx_var, (250, 150), (450, 300), 20)
    result = mlx_var.mlx.mlx_xpm_file_to_image(mlx_var.mlx_ptr, "images/drone1.xpm")
    mlx_var.drone_img.img, mlx_var.drone_img.w, mlx_var.drone_img.h = result
    mlx_var.drone_img.data, mlx_var.drone_img.bpp, mlx_var.drone_img.sl, mlx_var.drone_img.iformat = \
        mlx_var.mlx.mlx_get_data_addr(mlx_var.drone_img.img)
    print(mlx_var.drone_img.w, mlx_var.drone_img.h)
    copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img, (100, 100))

    # draw_square(mlx_var, (100, 200), 40)
    # draw_square(mlx_var, (300, 100), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 100), 40)
    # draw_square(mlx_var, (300, 300), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 300), 40)
    # draw_square(mlx_var, (400, 200), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 100), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 300), 40)

    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)
    mlx_var.mlx.mlx_loop_hook(mlx_var.mlx_ptr, drone_animation, mlx_var)
    mlx_var.mlx.mlx_loop(mlx_var.mlx_ptr)


def copy_img_to_buffer(buff_img: ImgData, img: ImgData, center: Tuple):
    x, y = center
    for i in range(0, (img.w * img.h * 4), 4):
        set_pixel(buff_img,
                  (x + (i % img.sl) // 4, y + i // img.sl),
                  rgbh_to_hex(
                       img.data[i + 0],
                       img.data[i + 1],
                       img.data[i + 2],
                       img.data[i + 3]
                  ))


def set_pixel(img: ImgData, center: Tuple, color: hex = 0xFFFFFFFF):
    x, y = center
    # print(f"x:{x}, y: {y}")
    if x < 0 or x > img.w or y < 0 or y > img.h:
        return
    pos = (y * img.sl) + (x * (img.bpp // 8))
    try:
        if img.data is not None:
            img.data[pos: pos + 4] = (color).to_bytes(4)
    except Exception as e:
        print((color).to_bytes(4))


if __name__ == "__main__":
    mlx_test()
