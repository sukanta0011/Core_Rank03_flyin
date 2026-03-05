from typing import Tuple
from pathlib import Path
from .base_mlx import MlxVarWithLetters, MyMLX
from .mlx_errors import (
    ImgError
)
from .image_operations import ImgData
from .image_operations import ImageOperations


class LetterToImageMapper:
    """Handles the extraction and mapping of font from a sprite sheet.

    This class parses a master XPM image containing alphanumeric characters
    and symbols, automatically calculating the tightest width for each
    character to support proportional font rendering.

    Attributes:
        mlx (MlxVarWithLetters): Container for MLX state and font maps.
        image (str): Path to the master sprite sheet XPM.
        letter_per_row (int): Number of characters per row in the sprite sheet.
        cap (str): String containing uppercase character order in sheet.
        small (str): String containing lowercase character order in sheet.
        num (str): String containing numeric character order in sheet.
        symbols (str): String containing special character order in sheet.
    """
    def __init__(self, mlx: MlxVarWithLetters) -> None:
        """Initializes the mapper and loads the master alphabet image."""
        self.mlx = mlx
        self.letter_per_row = 9
        self.cap = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.small = "abcdefghijklmnopqrstuvwxyz"
        self.num = "0123456789"
        self.symbols = ".,;:_#'!\"/?<>%&*()"
        base_path = Path(__file__).resolve().parent
        self.image = Path.joinpath(base_path, "alphabets.xpm")
        if self.image.exists():
            self.mlx.letter_img = ImageOperations.xmp_to_img(
                self.mlx, str(self.image))
        else:
            raise ImgError("'alphabets.xpm' file not found in 'mlx_tools")

    def create_map(self) -> None:
        """Triggers the full extraction process for all character sets.

        Maps capitals, small letters, numbers, and symbols based on hardcoded
        sprite sheet offsets. Also creates a default blank image for spaces.

        Raises:
            ImgError: If image generation or cropping fails during extraction.
        """
        w = 60  # Horizontal spacing between each letter
        h = 80  # Vertical spacing between each letter
        try:
            # all this parameters depends on the xpm image file
            # and need manual selection at first
            self.extract_different_letter_types(
                self.cap, 55, 45, 0, 30, w, h, 0)
            self.extract_different_letter_types(
                self.small, 55, 45, 0, 30, w, h, 264)
            self.extract_different_letter_types(
                self.num, 55, 45, 0, 30, w, h, 528)
            self.extract_different_letter_types(
                self.symbols, 55, 45, 0, 30, w, h, 712)
            self.mlx.base_letter_map[" "] = \
                ImageOperations.generate_blank_image(self.mlx, 30, 50)
            MyMLX.set_background(
                self.mlx.base_letter_map[" "], (0, 0),
                self.mlx.base_letter_map[" "].w,
                self.mlx.base_letter_map[" "].h,
                0x000000FF)
        except ImgError as e:
            raise ImgError(f"{type(e).__name__}: {e}")

    def extract_different_letter_types(self, symbols: str, crop_w: int,
                                       crop_h: int, x_off: int, y_off: int,
                                       w: int, h: int,
                                       vertical_off: int) -> None:
        """Calculates the minimal bounding box width for a character.

        Scans the pixel data from left-to-right and right-to-left to find the
        first non-black pixels, allowing for proportional text spacing.

        Args:
            img: The master sprite sheet image data.
            center: The (x, y) origin of the character cell.
            h: The height of the area to scan.
            w: The maximum width of the area to scan.

        Returns:
            Tuple[int, int]: A tuple of (left_offset, actual_width).
        """
        for id, letter in enumerate(symbols):
            x = id % self.letter_per_row
            y = id // self.letter_per_row
            new_x_off, width = self.extract_letter_width(
                self.mlx.letter_img, (
                    w * x + 2, h * y + y_off + vertical_off), crop_h, crop_w)
            # print(f"{letter}, x: {x}, off: {new_x_off}, w: {width}")
            self.crop_sub_image_from_image(
                letter, width, crop_h,
                (w * x + 2 + new_x_off, h * y + y_off + vertical_off))

    def extract_letter_width(self, img: ImgData, center: Tuple[int, int],
                             h: int, w: int) -> Tuple[int, int]:
        """Crops a specific glyph and stores it in the base_letter_map.

        Args:
            key: The character key (e.g., 'A', '!').
            w: The calculated width of the glyph.
            h: The height of the glyph.
            center: Top-left coordinate in the master image.
            color: Default foreground color (unused during crop).
            bg_color: Default background color (unused during crop).
        """
        start_x, start_y = center
        # print(f"Shared: {start_x, start_x + w}")
        left_width, right_width = img.w + 10, 0
        for y in range(start_y, start_y + h):
            x = start_x
            pos = y * img.sl + 4 * x
            # for x in range(start_x, start_x + w):
            while img.data is not None and (
                img.data[pos + 1] == 0 and
                img.data[pos + 2] == 0 and
                    img.data[pos + 3] == 0) and x < start_x + w:
                x += 1
                pos = y * img.sl + 4 * x
            if left_width > x:
                left_width = x

            x = start_x + w - 2
            pos = y * img.sl + 4 * x
            while img.data is not None and (
                img.data[pos + 1] == 0 and
                img.data[pos + 2] == 0 and
                    img.data[pos + 3] == 0) and x > start_x:
                x -= 1
                pos = y * img.sl + 4 * x
            if right_width < x:
                right_width = x
        left_width, right_width = left_width - 2, right_width + 2
        return (left_width - start_x, (right_width - left_width))

    def crop_sub_image_from_image(self, key: str, w: int, h: int,
                                  center: Tuple[int, int],
                                  color: int = 0xFFFFFFFF,
                                  bg_color: int = 0x00000000) -> None:
        self.mlx.base_letter_map[key] = ImageOperations.generate_blank_image(
            self.mlx, w, h)
        ImageOperations.crop_img(self.mlx.base_letter_map[key],
                                 self.mlx.letter_img, center)
