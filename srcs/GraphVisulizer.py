from typing import Tuple
import math
from mlx import Mlx


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


def draw_colormap(mlx_var):
    """Draw the colormap"""
    print("Drawing colormap...")
    for i in range(400):
        for j in range(400):
            r = int((0xFF * i) / 400)
            g = int((0xFF * j) / 400)
            b = int((0xFF * (400 - (i + j) // 2)) / 400)
            col = 0xFF000000 | (r << 16) | (g << 8) | b
            mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr, mlx_var.win_ptr, i, j, col)


def draw_circle(mlx_var: MlxVar, center: Tuple, radius: int):
    x, y = center
    for i in range(x - radius, x + radius):
        for j in range(y - radius, y + radius):
            curr_len = math.sqrt((i - x)**2 + (j - y)**2)
            if radius - 1 <= curr_len <= radius + 1:
                mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
                                          mlx_var.win_ptr, i, j, 0xFFFFFFFF)


def connect_two_circle(mlx_var: MlxVar, cen1: Tuple,
                       cen2: Tuple, radius: int, lines: int = 1):
    slope = (cen2[1] - cen1[1]) / (cen2[0] - cen1[0])
    print(f"slope: {slope}")
    for i in range(cen1[0] + radius, cen2[0] - radius):
        for j in range(cen1[1], cen2[1]):
            if (i - cen1[0]) != 0:
                curr_slope = (j - cen1[1]) / (i - cen1[0])
                # print(f"x: {i}, y: {j}, {curr_slope}")
                if curr_slope == slope:
                    mlx_var.mlx.mlx_pixel_put(
                        mlx_var.mlx_ptr, mlx_var.win_ptr, i, j, 0xFFFFFFFF)


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
    draw_circle(mlx_var, (100, 100), 40)
    draw_circle(mlx_var, (400, 200), 40)
    connect_two_circle(mlx_var, (100, 100), (400, 200), 40)

    mlx_var.mlx.mlx_loop(mlx_var.mlx_ptr)
