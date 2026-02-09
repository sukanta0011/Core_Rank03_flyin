from typing import Tuple, Dict
import math
from mlx import Mlx
from srcs.GraphConstructor import Zone

class MlxVar:
    def __init__(self) -> None:
        self.mlx = None
        self.mlx_ptr = None
        self.win_ptr = None


def mymouse(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def mykey(keynum, mlx_var):
    print(f"Got key {keynum}, and got my stuff back:")
    # print(mystuff)
    if keynum == 32:
        mlx_var.mlx.mlx_mouse_hook(mlx_var.win_ptr, None, None)


def gere_close(mlx_var):
    mlx_var.mlx.mlx_loop_exit(mlx_var.mlx_ptr)


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

def draw_square(mlx_var: MlxVar, center: Tuple, len: int):
    x, y = center
    draw_line(mlx_var, (x - len // 2, y + len // 2), len)
    draw_line(mlx_var, (x - len // 2, y - len // 2), len)
    draw_line(mlx_var, (x + len // 2, y - len // 2), len, "h")
    draw_line(mlx_var, (x - len // 2, y - len // 2), len, "h")


def connect_two_square(mlx_var: MlxVar, cen1: Tuple,
                       cen2: Tuple, len: int, lines: int = 1):
    if abs(cen2[0] - cen1[0]) == 0:
        draw_line(mlx_var, (cen1[0], cen2[0] + len // 2), cen2[1] - cen1[1] - len, "h")
    elif abs(cen2[1] - cen1[1]) == 0:
        draw_line(mlx_var, (cen1[0] + len // 2, cen1[1]), cen2[0] - cen1[0] - len)
    else:
        slope = (cen2[1] - cen1[1]) / (cen2[0] - cen1[0])
        for i in range(cen1[0] + len // 2, cen2[0] - len // 2):
            for j in range(cen1[1], cen2[1]):
                if (i - cen1[0]) != 0:
                    curr_slope = (j - cen1[1]) / (i - cen1[0])
                    if curr_slope == slope:
                        mlx_var.mlx.mlx_pixel_put(
                            mlx_var.mlx_ptr, mlx_var.win_ptr, i, j, 0xFFFFFFFF)


class GraphVisulizer:
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
    
    def generate_map(self):
        for _, zone in self.graph.items():
            coord = zone.coordinates
            x = coord[0] * 50 + 100
            y = coord[1] * 50 + self.h // 2
            draw_square(self.mlx, (x, y), 20)
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
    # draw_circle(mlx_var, (100, 100), 40)
    # draw_circle(mlx_var, (400, 200), 40)
    # connect_two_circle(mlx_var, (100, 100), (400, 200), 40)
    draw_square(mlx_var, (100, 100), 40)
    draw_square(mlx_var, (100, 300), 40)
    connect_two_square(mlx_var, (100, 100), (100, 300), 40)


    mlx_var.mlx.mlx_loop(mlx_var.mlx_ptr)
