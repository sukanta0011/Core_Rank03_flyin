from typing import Tuple, Dict, List
import math
from mlx import Mlx
from webcolors import name_to_hex
from srcs.GraphConstructor import Zone

class MlxVar:
    def __init__(self) -> None:
        self.mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.img = None


def mymouse(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def mykey(keynum, mlx_var):
    print(f"Got key {keynum}, and got my stuff back:")
    # print(mystuff)
    if keynum == 32:
        mlx_var.mlx.mlx_mouse_hook(mlx_var.win_ptr, None, None)


def gere_close(mlx_var):
    mlx_var.mlx.mlx_loop_exit(mlx_var.mlx_ptr)


def rgb_to_hex(r: int = 0, g: int = 0, b: int = 0):
    return 0xFF000000 | r << 16 | g << 8 | b


def color_name_to_code(color_name) -> str:
    try:
        color_code = name_to_hex(color_name)
        if "#000000" not in color_code:
            return color_code
        else:
            return "#ffffff"
    except ValueError:
        return "#ffffff"


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
    if direction == "v":
        for i in range(x, x + len):
            mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
                                    mlx_var.win_ptr, i, y, color)
    elif direction == "h":
        for i in range(y, y + len):
            mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
                                    mlx_var.win_ptr, x, i, color)
    else:
        print(f"Unknown direction: {direction}. "
              "Allowed directions are 'v' and 'h'")


def draw_square(mlx_var: MlxVar, center: Tuple,
                len: int, color: hex = 0xFFFFFFFF):
    x, y = center
    draw_line(mlx_var, (x - len // 2, y + len // 2), len, "v", color)
    draw_line(mlx_var, (x - len // 2, y - len // 2), len, "v", color)
    draw_line(mlx_var, (x + len // 2, y - len // 2), len, "h", color)
    draw_line(mlx_var, (x - len // 2, y - len // 2), len, "h", color)


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
                        mlx_var.mlx.mlx_pixel_put(
                            mlx_var.mlx_ptr, mlx_var.win_ptr, i, j, color)


class GraphVisualizer:
    def __init__(self, graph: Dict[str, Zone], w: int, h: int):
        self.graph = graph
        self.w = w
        self.h = h
        self.mlx = MlxVar()
        self.init_mlx()

    def init_mlx(self):
        self.mlx.mlx = Mlx()
        self.mlx.mlx_ptr = self.mlx.mlx.mlx_init()
        self.mlx.win_ptr = self.mlx.mlx.mlx_new_window(self.mlx.mlx_ptr, self.w, self.h, "Fly IN")
        self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        self.mlx.mlx.mlx_mouse_hook(self.mlx.win_ptr, mymouse, self.mlx)
        self.mlx.mlx.mlx_key_hook(self.mlx.win_ptr, mykey, self.mlx)
        self.mlx.mlx.mlx_hook(self.mlx.win_ptr, 33, 0, gere_close, self.mlx)

    def start_mlx(self):
        self.mlx.mlx.mlx_loop(self.mlx.mlx_ptr)

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
        # image_loc = "images/drone1.xpm"
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
                hex_str = color_name_to_code(zone.color)
                color = 0xFF000000 | int(hex_str[1:], 16)
            self.draw_all_zones(self.mlx, (xi, yi), sq_len,
                                zone.name, color, zone.capacity)
            self.fill_zone_wih_drones(self.mlx, sq_len // 2, (xi, yi),
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
                            sq_len, rgb_to_hex(g=255))
                    elif link.target.zone_type.value == "restricted":
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), sq_len,
                            rgb_to_hex(b=255))
                    else:
                        connect_two_square(
                            self.mlx, (xi, yi), (xf, yf), sq_len)
                else:
                    connect_two_square(
                        self.mlx, (xi, yi), (xf, yf), sq_len,
                        rgb_to_hex(r=255))

        self.start_mlx()


def mlx_test():
    mlx_var = MlxVar()
    mlx_var.mlx = Mlx()
    mlx_var.mlx_ptr = mlx_var.mlx.mlx_init()
    mlx_var.win_ptr = mlx_var.mlx.mlx_new_window(mlx_var.mlx_ptr, 600, 400, "win title")
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    # mlx_var.mlx.mlx_string_put(mlx_var.mlx_ptr, mlx_var.win_ptr, 10, 10, 255, "Hello PyMlx!")
    (ret, w, h) = mlx_var.mlx.mlx_get_screen_size(mlx_var.mlx_ptr)
    print(f"Got screen size: {w} x {h} .")

    stuff = [1, 2]
    mlx_var.mlx.mlx_mouse_hook(mlx_var.win_ptr, mymouse, stuff)
    mlx_var.mlx.mlx_key_hook(mlx_var.win_ptr, mykey, mlx_var)
    mlx_var.mlx.mlx_hook(mlx_var.win_ptr, 33, 0, gere_close, mlx_var)
    # draw_colormap(mlx_var)
    draw_square(mlx_var, (200, 150), 20)
    draw_square(mlx_var, (250, 300), 20)
    connect_two_square(mlx_var, (200, 150), (250, 300), 20)
    draw_square(mlx_var, (250, 150), 20)
    draw_square(mlx_var, (450, 300), 20)
    connect_two_square(mlx_var, (250, 150), (450, 300), 20)
    result = mlx_var.mlx.mlx_xpm_file_to_image(mlx_var.mlx_ptr, "images/drone1.xpm")
    mlx_var.img, _, _ = result
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr, mlx_var.img, 100, 100)
    # draw_square(mlx_var, (100, 200), 40)
    # draw_square(mlx_var, (300, 100), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 100), 40)
    # draw_square(mlx_var, (300, 300), 40)
    # connect_two_square(mlx_var, (100, 200), (300, 300), 40)
    # draw_square(mlx_var, (400, 200), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 100), 40)
    # connect_two_square(mlx_var, (400, 200), (300, 300), 40)
    mlx_var.mlx.mlx_loop(mlx_var.mlx_ptr)


if __name__ == "__main__":
    mlx_test()
