from typing import Dict, Tuple
from webcolors import name_to_hex
from mlx import Mlx
from srcs.mlx_tools.ImageOperations import ImgData, generate_blank_image


class MlxVar:
    def __init__(self) -> None:
        self.mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.screen_w = 0
        self.screen_h = 0
        self.buff_img = ImgData()
        self.static_bg = ImgData()
        self.drone_img = ImgData()
        self.animation_counter = 0
        self.letter_img = ImgData()
        self.letter_map: Dict[str, ImgData] = {}


class MyMLX:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.mlx = MlxVar()
        self.init_mlx()

    def init_mlx(self):
        self.mlx.mlx = Mlx()
        self.mlx.mlx_ptr = self.mlx.mlx.mlx_init()
        self.mlx.win_ptr = self.mlx.mlx.mlx_new_window(
            self.mlx.mlx_ptr, self.w, self.h, "GUI")
        self.mlx.buff_img = generate_blank_image(self.mlx, self.w, self.h)
        self.mlx.static_bg = generate_blank_image(self.mlx, self.w, self.h)
        self.set_background(self.mlx.static_bg)
        # print(f"Buffer image: {self.mlx.mlx.mlx_get_data_addr(self.mlx.buff_img.img)}")
        self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        self.mlx.mlx.mlx_mouse_hook(self.mlx.win_ptr, self.mymouse, self.mlx)
        self.mlx.mlx.mlx_key_hook(self.mlx.win_ptr, self.mykey, self.mlx)
        self.mlx.mlx.mlx_hook(self.mlx.win_ptr, 33, 0,
                              self.gere_close, self.mlx)

    def get_mlx(self) -> MlxVar:
        return self.mlx

    def start_mlx(self):
        self.mlx.mlx.mlx_loop(self.mlx.mlx_ptr)

    def stop_mlx(self):
        self.mlx.mlx.mlx_loop_exit(self.mlx.mlx_ptr)
        self.mlx.mlx.mlx_destroy_image(self.mlx.mlx, self.mlx.buff_img.img)
        self.mlx.mlx.mlx_destroy_image(self.mlx.mlx, self.mlx.static_bg.img)
        self.mlx.mlx.mlx_destroy_window(self.mlx.mlx, self.mlx.win_ptr)

    def mymouse(self, button, x, y, mystuff):
        print(f"Got mouse event! button {button} at {x},{y}.")

    def mykey(self, keynum, mlx_var):
        pass
        # print(f"Got key {keynum}, and got my stuff back:")
        # if keynum == 112:
        #     print("Next Move")

    def gere_close(self, mlx_var):
        mlx_var.mlx.mlx_loop_exit(mlx_var.mlx_ptr)

    def put_buffer_image(self):
        if self.mlx.buff_img is not None:
            self.mlx.mlx.mlx_put_image_to_window(
                self.mlx.mlx_ptr, self.mlx.win_ptr, self.mlx.buff_img.img,
                0, 0)
        else:
            print("Error: buffer image is not set")

    def set_background(self, img: ImgData, color=0xFF000000):
        pixel_bytes = color.to_bytes(4, 'little')
        img.data[:] = pixel_bytes * (img.h * img.w)

    def rgb_to_hex(self, r: int = 0, g: int = 0, b: int = 0):
        return 0xFF000000 | r << 16 | g << 8 | b

    def color_name_to_code(self, color_name) -> str:
        try:
            color_code = name_to_hex(color_name)
            if "#000000" not in color_code:
                return color_code
            else:
                return "#ffffff"
        except ValueError:
            return "#ffffff"
