from __future__ import annotations
from typing import List, Tuple, Protocol, TYPE_CHECKING
if TYPE_CHECKING:
    from srcs.mlx_tools.BaseMLX import MlxVar


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


def generate_blank_image(mlx: MlxVar, w: int, h: int) -> ImgData:
    if w <= 0 or h <= 0:
        print("Error: Blank image generation failed"
              f"Wrong w and h has to be positive ({w}, {h})")
        return None
    new_img = ImgData()
    new_img.h = int(h)
    new_img.w = int(w)
    new_img.img = mlx.mlx.mlx_new_image(mlx.mlx_ptr, new_img.w, new_img.h)
    new_img.data, new_img.bpp, new_img.sl, new_img.iformat = \
        mlx.mlx.mlx_get_data_addr(new_img.img)
    return new_img


def xmp_to_img(mlx: MlxVar, image_loc: str) -> ImgData:
    try:
        img = ImgData()
        result = mlx.mlx.mlx_xpm_file_to_image(mlx.mlx_ptr, image_loc)
        img.img, img.w, img.h = result
        img.data, img.bpp, img.sl, img.iformat = \
            mlx.mlx.mlx_get_data_addr(img.img)
        return img
    except Exception as e:
        print(f"Error: Unable to open image, {e}")
        return None


def copy_img(dest: ImgData, src: ImgData, center: Tuple):
    start_x, start_y = center
    if (start_x + src.w > dest.w) or (start_y + src.h > dest.h):
        return
    for y in range(src.h):
        dest_start = (start_y + y) * dest.sl + (4 * start_x)
        dest_end = dest_start + (4 * src.w)
        src_start = y * src.sl
        src_end = src_start + (src.w * 4)
        dest.data[dest_start:dest_end] = src.data[src_start:src_end]


def crop_img(dest: ImgData, src: ImgData, center: Tuple):
    start_x, start_y = center
    for y in range(dest.h):
        dest_start = y * dest.sl
        dest_end = dest_start + (4 * dest.w)
        src_start = (start_y + y) * src.sl + (4 * start_x)
        src_end = src_start + (4 * dest.w)
        dest.data[dest_start:dest_end] = src.data[src_start:src_end]


def extract_letter_width(img: ImgData, center: Tuple,
                         h: int, w: int) -> Tuple[int, int]:
    start_x, start_y = center
    left_width, right_width = img.w + 10, start_x
    for y in range(h):
        src_start = (start_y + y) * img.sl + (4 * start_x)
        src_end = src_start + (4 * w)
        while (img.data[src_start + 1] == 0 and
               img.data[src_start + 2] == 0 and
                img.data[src_start + 3] == 0) and\
                (src_start <= src_end):
            src_start += 4
        if left_width > src_start - 4:
            left_width = src_start - 4

        if src_start < src_end:
            while (img.data[src_start + 1] > 0 or 
                   img.data[src_start + 2] > 0 or
                    img.data[src_start + 3] > 0) and\
                     (src_start <= src_end):
                src_start += 4
            if right_width < src_start - 4:
                right_width = src_start - 4
    return (left_width, right_width)


def set_pixel(img: ImgData, center: int | Tuple, color= 0xFFFFFFFF):
    if isinstance(center, int):
        # print(f"one position: {center}")
        pos = center
        if pos >= (img.w * img.h * 4):
            return
    elif isinstance(center, Tuple):
        if len(center) == 2:
            x, y = center
            # print(f"x:{x}, y: {y}")
            if x < 0 or x > img.w or y < 0 or y > img.h:
                print(f"pixel outside range, x:{x}, y: {y}")
                return
            pos = (y * img.sl) + (x * (img.bpp // 8))
        else:
            print(f"Error: Invalid center format {center}. Allowed (x, y)")
            return
    else:
        print(f"Error: Invalid center instance {center}. "
              "Allowed instances are int/Tuple")
        return

    try:
        if img.data is not None:
            img.data[pos: pos + 4] = (color).to_bytes(4, 'little')
    except Exception as e:
        # pass
        print(f"Error: {e}")


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
            print(f"Error: Factor has to be bigger than 0, not {factor}")
            return
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
        new_img = generate_blank_image(mlx, img.w, img.h)
        for i in range(0, new_img.h * new_img.w * 4, 4):
            if img.data[i + 1] == 0 and img.data[i + 2] == 0 and \
                    img.data[i + 3] == 0:
                new_img.data[i: i + 4] = \
                    (bg_color).to_bytes(4, "little")
            else:
                new_img.data[i: i + 4] = (font_color).to_bytes(4, "little")
        return new_img


class TxtToImage:
    def __init__(self, letter_map: Dict[str, ImgData]) -> None:
        self.stages: List[Stages] = []
        self.letter_map = letter_map
        self.letter_dict: Dict[str, ImgData] = {}

    def add_stages(self, stage: Stages):
        self.stages.append(stage)

    def print_txt(self, mlx: MlxVar, buff_img: ImgData, txt: str,
                  origin: Tuple, factor: float = 1.0, font_color=0xFFFFFFFF,
                  bg_color=0x00000000):
        x, y = origin
        for letter in txt:
            comb_key = f"{letter}_{factor}_{font_color}_{bg_color}"
            img = self.letter_dict.get(comb_key)
            if img is None:
                try:
                    img = self.letter_map[letter]
                except KeyError:
                    img = self.letter_map[" "]
                for stage in self.stages:
                    img = stage.process(mlx, img, factor, font_color, bg_color)
                if img is not None:
                    self.letter_dict[comb_key] = img
            copy_img(buff_img, img, (x, y))
            x += img.w


def tester():
    mlx = MyMLX(800, 800)
    # image = "images/alphabets.xpm"
    letter_map = LetterToImageMapper(mlx.mlx)
    # copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_img, (0, 0))
    letter_map.create_map()
    copy_img(mlx.mlx.buff_img, mlx.mlx.letter_map["A"], (0, 0))
    copy_img(mlx.mlx.buff_img, mlx.mlx.letter_map["e"], (50, 0))
    copy_img(mlx.mlx.buff_img, mlx.mlx.letter_map["1"], (150, 0))
    copy_img(mlx.mlx.buff_img, mlx.mlx.letter_map["("], (100, 0))
    copy_img(mlx.mlx.buff_img, mlx.mlx.letter_map[")"], (200, 0))
    scaler = ImageScaler()
    scaled_a = scaler.process(mlx.mlx, mlx.mlx.letter_map["A"], 0.3)
    copy_img(mlx.mlx.buff_img, scaled_a, (250, 0))

    letter_color = TxtColorChanger()
    colored_a = letter_color.process(mlx.mlx, mlx.mlx.letter_map["A"])

    txt_to_img = TxtToImage(mlx.mlx.letter_map)
    txt_to_img.add_stages(scaler)
    txt_to_img.add_stages(letter_color)
    txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img, "Hello Mr._(0071)",
                         (100, 100))

    copy_img(mlx.mlx.buff_img, colored_a, (300, 0))

    mlx.mlx.mlx.mlx_put_image_to_window(mlx.mlx.mlx_ptr, mlx.mlx.win_ptr,
                                        mlx.mlx.buff_img.img, 0, 0)
    mlx.start_mlx()


if __name__ == "__main__":
    tester()
