from typing import Dict, List, Tuple, Protocol
from mlx import Mlx
from srcs.GraphVisualizer import (
    MlxVar, MyMLX, copy_img_to_buffer,
    ImgData, crop_letter, generate_blank_image,
    xmp_to_img)


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
                                  center: Tuple, color =0xFFFFFFFF,
                                  bg_color = 0x00000000):
        self.mlx.letter_map[key] = generate_blank_image(self.mlx, w, h)
        crop_letter(self.mlx.letter_map[key],
                    self.mlx.letter_img, center, color, bg_color)


class Stages(Protocol):
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color=0xFFFFFFFF,
                bg_color=0x00000000) -> ImgData:
        pass


class ImageScaler:
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color=0xFFFFFFFF,
                bg_color=0x00000000) -> ImgData:
        if factor <= 0:
            print(f"Error: Factor has to be bigger than 0, not {self.factor}")
        if factor == 1:
            return img
        new_img = generate_blank_image(mlx, int(img.w * factor),
                                       int(img.h * factor))
        for y in range(new_img.h):
            for x in range(new_img.w):
                new_img_pos = y * new_img.sl + (4 * x)
                img_pos = int(y / factor) * img.sl + \
                    (4 * int(x / factor))
                # print(img_pos)
                new_img.data[new_img_pos: new_img_pos + 4] = \
                    img.data[img_pos: img_pos + 4]
        return new_img


class TxtColorChanger:
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color=0xFFFFFFFF,
                bg_color=0x00000000) -> ImgData:
        if font_color == 0xFFFFFFFF and bg_color == 0x00000000:
            return img
        new_img = generate_blank_image(mlx, img.w, img.h)
        crop_letter(new_img, img, (0, 0), font_color, bg_color)
        return new_img


class TxtToImage:
    def __init__(self, letter_map: Dict[str, ImgData]) -> None:
        self.stages = []
        self.letter_map = letter_map

    def add_stages(self, stage: Stages):
        self.stages.append(stage)

    def print_txt(self, mlx: MlxVar, buff_img: ImgData, txt: str,
                  origin: Tuple, factor: float = 1.0, font_color=0xFFFFFFFF,
                  bg_color=0x00000000):
        x, y = origin
        for letter in txt:
            try:
                img = self.letter_map[letter]
            except KeyError:
                img = self.letter_map[" "]
            for stage in self.stages:
                img = stage.process(mlx, img, factor, font_color, bg_color)
            copy_img_to_buffer(buff_img, img, (x, y))
            x += img.w


def tester():
    mlx = MyMLX(800, 800)
    # image = "images/alphabets.xpm"
    letter_map = LetterToImageMapper(mlx.mlx)
    # copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_img, (0, 0))
    letter_map.create_map()
    copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_map["A"], (0, 0))
    copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_map["e"], (50, 0))
    copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_map["1"], (150, 0))
    copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_map["("], (100, 0))
    copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_map[")"], (200, 0))
    scaler = ImageScaler()
    scaled_a = scaler.process(mlx.mlx, mlx.mlx.letter_map["A"], 0.3)
    copy_img_to_buffer(mlx.mlx.buff_img, scaled_a, (250, 0))

    letter_color = TxtColorChanger()
    colored_a = letter_color.process(mlx.mlx, mlx.mlx.letter_map["A"])

    txt_to_img = TxtToImage(mlx.mlx.letter_map)
    txt_to_img.add_stages(scaler)
    txt_to_img.add_stages(letter_color)
    txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img, "Hello Mr._(0071)",
                         (100, 100))

    copy_img_to_buffer(mlx.mlx.buff_img, colored_a, (300, 0))

    mlx.mlx.mlx.mlx_put_image_to_window(mlx.mlx.mlx_ptr, mlx.mlx.win_ptr,
                                        mlx.mlx.buff_img.img, 0, 0)
    mlx.start_mlx()


if __name__ == "__main__":
    tester()
