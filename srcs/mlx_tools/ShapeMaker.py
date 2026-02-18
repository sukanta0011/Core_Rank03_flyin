import math
from typing import Tuple
from srcs.mlx_tools.BaseMLX import MlxVar
from srcs.mlx_tools.ImageOperations import set_pixel, ImgData


class ShapeGenerator:
    def __init__(self, mlx_var: MlxVar) -> None:
        self.mlx_var = mlx_var

    def draw_circle(self, center: Tuple, radius: int):
        x, y = center
        for i in range(x - radius, x + radius):
            for j in range(y - radius, y + radius):
                curr_len = math.sqrt((i - x)**2 + (j - y)**2)
                if radius - 1 <= curr_len <= radius + 1:
                    self.mlx_var.mlx.mlx_pixel_put(
                        self.mlx_var.mlx_ptr, self.mlx_var.win_ptr,
                        i, j, 0xFFFFFFFF)

    def draw_line(self, img: ImgData, coordinate: Tuple,
                  len: int, direction: str = "v",
                  color=0xFFFFFFFF) -> None:
        x, y = coordinate
        if direction == "h":
            for i in range(x, x + len):
                set_pixel(img, (i, y), color)
        elif direction == "v":
            for i in range(y, y + len):
                set_pixel(img, (x, i), color)
        else:
            print(f"Unknown direction: {direction}. "
                  "Allowed directions are 'v' and 'h'")

    def draw_square(self, img: ImgData, center: Tuple,
                    len: int, color=0xFFFFFFFF):
        x, y = center
        self.draw_line(img, (x - len // 2, y + len // 2), len, "h", color)
        self.draw_line(img, (x - len // 2, y - len // 2), len, "h", color)
        self.draw_line(img, (x + len // 2, y - len // 2), len, "v", color)
        self.draw_line(img, (x - len // 2, y - len // 2), len, "v", color)

    def draw_rectangle(self, img: ImgData, center: Tuple,
                       h: int, w: int, color=0xFFFFFFFF):
        x, y = center
        for i in range(y, y + h):
            self.draw_line(img, (x, i), h, "h", color)

    def connect_two_square(
            self, img: ImgData, cen1: Tuple,
            cen2: Tuple, len: int, color=0xFFFFFFFF):
        if cen1[0] > cen2[0]:
            x_max, x_min = cen1[0], cen2[0]
        else:
            x_max, x_min = cen2[0], cen1[0]
        if cen1[1] > cen2[1]:
            y_max, y_min = cen1[1], cen2[1]
        else:
            y_max, y_min = cen2[1], cen1[1]

        if x_max - x_min == 0:
            self.draw_line(img, (x_min, y_min + len // 2),
                           y_max - y_min - len, "v", color)
        elif y_max - y_min == 0:
            self.draw_line(img, (x_min + len // 2, y_min),
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
                                self.draw_rectangle(img, (i, j), 1, 1, color)
                            else:
                                self.draw_rectangle(img, (i, j), 1, 1, color)
