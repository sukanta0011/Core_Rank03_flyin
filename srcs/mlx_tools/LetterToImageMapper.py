from typing import Tuple
from srcs.mlx_tools.BaseMLX import MlxVar
from srcs.mlx_tools.ImageOperations import (
    xmp_to_img, crop_img,
    generate_blank_image)


class LetterToImageMapper:
    def __init__(self, mlx: MlxVar) -> None:
        self.mlx = mlx
        self.image = "images/alphabets.xpm"
        self.cap = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.small = "abcdefghijklmnopqrstuvwxyz"
        self.num = "0123456789"
        self.symbols = ".,;:_#'!\"/?<>%&*()"
        self.mlx.letter_img = xmp_to_img(self.mlx, self.image)

    def create_map(self):
        w = 60
        h = 80
        self.extract_different_letter_types(
            self.cap, 40, 50, 15, 30, w, h, 0)
        self.extract_different_letter_types(
            self.small, 25, 50, 20, 30, w, h, 264)
        self.extract_different_letter_types(
            self.num, 30, 50, 15, 30, w, h, 528)
        self.extract_different_letter_types(
            self.symbols, 20, 50, 22, 30, w, h, 712)

    def extract_different_letter_types(self, symbols: str, crop_w: int,
                                       crop_h: int, x_off: int, y_off: int,
                                       w: int, h: int, vertical_off: int):
        for id, letter in enumerate(symbols):
            x = id % 9
            y = id // 9
            self.crop_sub_image_from_image(
                letter, crop_w, crop_h,
                (w * x + x_off, h * y + y_off + vertical_off))

    def crop_sub_image_from_image(self, key: str, w: int, h: int,
                                  center: Tuple, color=0xFFFFFFFF,
                                  bg_color=0x00000000):
        self.mlx.letter_map[key] = generate_blank_image(self.mlx, w, h)
        crop_img(self.mlx.letter_map[key],
                 self.mlx.letter_img, center)
