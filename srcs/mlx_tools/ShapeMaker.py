class ShapeGenerator:
    def draw_circle(self, mlx_var: MlxVar, center: Tuple, radius: int):
        x, y = center
        for i in range(x - radius, x + radius):
            for j in range(y - radius, y + radius):
                curr_len = math.sqrt((i - x)**2 + (j - y)**2)
                if radius - 1 <= curr_len <= radius + 1:
                    mlx_var.mlx.mlx_pixel_put(mlx_var.mlx_ptr,
                                            mlx_var.win_ptr, i, j, 0xFFFFFFFF)

    def draw_line(self, mlx_var: MlxVar, coordinate: Tuple,
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

    def draw_square(self, mlx_var: MlxVar, center: Tuple,
                    len: int, color: hex = 0xFFFFFFFF):
        x, y = center
        self.draw_line(mlx_var, (x - len // 2, y + len // 2), len, "h", color)
        self.draw_line(mlx_var, (x - len // 2, y - len // 2), len, "h", color)
        self.draw_line(mlx_var, (x + len // 2, y - len // 2), len, "v", color)
        self.draw_line(mlx_var, (x - len // 2, y - len // 2), len, "v", color)

    def draw_rectangle(self, mlx_var: MlxVar, center: Tuple,
                       h: int, w: int, color: hex = 0xFFFFFFFF):
        x, y = center
        for i in range(y, y + h):
            self.draw_line(mlx_var, (x, i), h, "h", color)

    def connect_two_square(
            self, mlx_var: MlxVar, cen1: Tuple,
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
            self.draw_line(mlx_var, (x_min, y_min + len // 2),
                    y_max - y_min - len, "v", color)
        elif y_max - y_min == 0:
            self.draw_line(mlx_var, (x_min + len // 2, y_min),
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
                                self.draw_rectangle(mlx_var, (i, j), 1, 1, color)
                            else:
                                self.draw_rectangle(mlx_var, (i, j), 1, 1, color)