from typing import Tuple
from .base_mlx import MlxVar
from .mlx_errors import (
    ParametersError, ImgError
)
from .image_operations import ImageOperations, ImgData


class ShapeGenerator:
    """Static utility class for drawing geometric primitives onto
    image buffers.

    This class provides methods to render basic shapes like lines,
    hollow squares, and filled rectangles by directly manipulating
    the underlying pixel data
    of an ImgData object.
    """
    @staticmethod
    def draw_line(mlx_var: MlxVar, img: ImgData, coordinate: Tuple[int, int],
                  len: int, direction: str = "v",
                  color: int = 0xFFFFFFFF, thickness: int = 1) -> None:
        """Draws a horizontal or vertical line with specified thickness.

        Args:
            mlx_var: The MLX state container.
            img: The destination image buffer.
            coordinate: The starting (x, y) position of the line.
            len: The length of the line in pixels.
            direction: 'h' for horizontal, 'v' for vertical.
            color: Hexadecimal color (ARGB).
            thickness: Width of the line in pixels.

        Raises:
            ParametersError: If coordinates are non-integers, out of range,
                or if an invalid direction is provided.
        """
        x, y = coordinate
        if not isinstance(x, int) or not isinstance(y, int):
            raise ParametersError(
                "Drawing line failed, center coordinate need to be "
                f"integer ({coordinate})")
        if direction == "h":
            draw_start = max(0, x)
            draw_end = min(img.w, x + len)

            y_start = y - (thickness // 2)
            for i in range(thickness):
                if y_start + i < 0 or y_start + i >= img.h:
                    continue
                if draw_start < draw_end:
                    for j in range(draw_start, draw_end):
                        ImageOperations.set_pixel(img, (j, y_start + i), color)
        elif direction == "v":
            draw_start = max(0, y)
            draw_end = min(img.h, y + len)
            x_start = x - thickness // 2
            for i in range(thickness):
                if x_start + i < 0 or x_start + i >= img.w:
                    continue
                for j in range(draw_start, draw_end):
                    ImageOperations.set_pixel(img, (x_start + i, j), color)
        else:
            raise ParametersError(f"Drawing line failed. Unknown direction: "
                  f"{direction}. Allowed directions are 'v' and 'h'")

    @staticmethod
    def draw_hollow_square(mlx_var: MlxVar, img: ImgData,
                           center: Tuple[int, int],
                           len: int, color: int = 0xFFFFFFFF) -> None:
        """Draws a hollow square centered around a specific coordinate.

        Constructs the square by calling `draw_line` for each of the
        four sides.

        Args:
            mlx_var: The MLX state container.
            img: The destination image buffer.
            center: The (x, y) center point of the square.
            len: The side length of the square.
            color: Hexadecimal color (ARGB).

        Raises:
            ImgError: If the square exceeds image boundaries or
            calculation fails.
        """
        try:
            x, y = center
            if not isinstance(x, int) or not isinstance(y, int):
                raise ParametersError(
                    "Drawing hollow square failed. center coordinate need "
                    f"to be integer ({center})")
            ShapeGenerator.draw_line(
                mlx_var, img, (x - len // 2, y + len // 2), len, "h", color)
            ShapeGenerator.draw_line(
                mlx_var, img, (x - len // 2, y - len // 2), len, "h", color)
            ShapeGenerator.draw_line(
                mlx_var, img, (x + len // 2, y - len // 2), len, "v", color)
            ShapeGenerator.draw_line(
                mlx_var, img, (x - len // 2, y - len // 2), len, "v", color)
        except Exception as e:
            raise ImgError(f"Drawing hollow square failed.-> {e}")

    @staticmethod
    def draw_filled_rectangle(mlx_var: MlxVar, img: ImgData,
                              center: Tuple[int, int], h: int, w: int,
                              color: int = 0xFFFFFFFF) -> None:
        """Draws a solid filled rectangle.

        Args:
            mlx_var: The MLX state container.
            img: The destination image buffer.
            center: The (x, y) top-left coordinate of the rectangle.
            h: Height of the rectangle.
            w: Width of the rectangle.
            color: Hexadecimal color (ARGB).

        Raises:
            ImgError: If the rectangle exceeds image boundaries.
        """
        try:
            x, y = center
            if not isinstance(x, int) or not isinstance(y, int):
                raise ParametersError(
                    "Drawing filled rectangle failed. center coordinate "
                    f"need to be integer ({center})")
            for i in range(y, y + h):
                ShapeGenerator.draw_line(mlx_var, img, (x, i), w, "h", color)
        except Exception as e:
            raise ImgError(f"Drawing filled rectangle failed.-> {e}")

    @staticmethod
    def connect_two_square(mlx_var: MlxVar,
            img: ImgData, cen1: Tuple,
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
            ShapeGenerator.draw_line(mlx_var, img, (x_min, y_min + len // 2),
                           y_max - y_min - len, "v", color)
        elif y_max - y_min == 0:
            ShapeGenerator.draw_line(mlx_var, img, (x_min + len // 2, y_min),
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
                                ShapeGenerator.draw_filled_rectangle(mlx_var, img, (i, j), 1, 1, color)
                            else:
                                ShapeGenerator.draw_filled_rectangle(mlx_var, img, (i, j), 1, 1, color)
