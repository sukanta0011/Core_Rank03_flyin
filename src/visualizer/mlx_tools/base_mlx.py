from typing import Dict, Tuple, Any
from webcolors import name_to_hex
from mlx import Mlx
from .mlx_errors import MLXError
from .image_operations import ImgData, ImageOperations


class MlxVar:
    """MLX module variable to store mlx graphics library variables"""
    def __init__(self) -> None:
        self.mlx = Mlx()
        self.mlx_ptr = None
        self.win_ptr = None
        self.screen_w = 0
        self.screen_h = 0
        self.buff_img = ImgData()
        self.static_bg = ImgData()
        self.drone_img = ImgData()


class MlxVarWithLetters(MlxVar):
    """Child class of MLX variable with additional image storing option"""
    def __init__(self) -> None:
        super().__init__()
        self.letter_img = ImgData()
        self.base_letter_map: Dict[str, ImgData] = {}
        self.extended_letter_map: Dict[str, ImgData] = {}


class MyMLX:
    """A wrapper class for MiniLibX (MLX) to handle windowing and
    image buffering.

    This class manages the lifecycle of an MLX instance, including window
    initialization, event hooks (mouse, keyboard, window close), and
    double-buffering via static and dynamic image buffers.

    Attributes:
        name (str): The title of the MLX window.
        w (int): Width of the window in pixels.
        h (int): Height of the window in pixels.
        mlx (MlxVarWithLetters): Custom container for MLX pointers
        and image data.
    """

    def __init__(self, name: str, w: int, h: int) -> None:
        """Initializes MyMLX with window dimensions and sets up the
        MLX environment."""

        self.name = name
        self.w = w
        self.h = h
        self.mlx = MlxVarWithLetters()
        self.init_mlx()

    def init_mlx(self) -> None:
        """Initializes the MLX pointer, creates a window, and prepares
        image buffers.

        Sets up mouse, keyboard, and window close hooks.

        Raises:
            MLXError: If MLX initialization, window creation, or buffer
                allocation fails.
        """
        try:
            self.mlx.mlx_ptr = self.mlx.mlx.mlx_init()
            self.mlx.win_ptr = self.mlx.mlx.mlx_new_window(
                self.mlx.mlx_ptr, self.w, self.h, self.name)
            self.mlx.buff_img = ImageOperations.generate_blank_image(
                self.mlx, self.w, self.h)
            self.mlx.static_bg = ImageOperations.generate_blank_image(
                self.mlx, self.w, self.h)
            self.set_background(self.mlx.buff_img, (0, 0), self.w, self.h)
            self.set_background(self.mlx.static_bg, (0, 0), self.w, self.h)
            # print(f"Buffer image: {self.mlx.mlx.mlx_get_data_addr(
            # self.mlx.buff_img.img)}")
            self.mlx.mlx.mlx_clear_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
            self.mlx.mlx.mlx_mouse_hook(self.mlx.win_ptr,
                                        self.mymouse, self.mlx)
            self.mlx.mlx.mlx_key_hook(self.mlx.win_ptr, self.mykey, self.mlx)
            self.mlx.mlx.mlx_hook(self.mlx.win_ptr, 33, 0,
                                  self.stop_mlx, self.mlx)
        except Exception as e:
            raise MLXError(
                f"Mlx initialization failed. {type(e).__name__}: {e}")

    def get_mlx(self) -> MlxVar:
        """Returns the current MLX variable container.

        Returns:
            MlxVar: The object containing MLX pointers and state.
        """
        return self.mlx

    def start_mlx(self) -> None:
        """Enters the MLX main event loop. This is a blocking call."""
        self.mlx.mlx.mlx_loop(self.mlx.mlx_ptr)

    def stop_mlx(self, mlx_var: MlxVar) -> None:
        """Exits the MLX loop and triggers resource cleanup.

        Args:
            mlx_var (MlxVar): The MLX state container.
        """
        self.mlx.mlx.mlx_loop_exit(self.mlx.mlx_ptr)
        # self.clean_mlx()

    def clean_mlx(self) -> None:
        """Destroys all allocated MLX images and the window to prevent
        memory leaks.

        Iterates through the letter maps and buffer images to free
        graphical memory.
        """
        if self.mlx.buff_img.img is not None:
            self.mlx.mlx.mlx_destroy_image(
                self.mlx.mlx_ptr, self.mlx.buff_img.img)
        if self.mlx.static_bg.img is not None:
            self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr,
                                           self.mlx.static_bg.img)
        if self.mlx.drone_img.img is not None:
            self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr,
                                           self.mlx.drone_img.img)
        if self.mlx.letter_img.img is not None:
            self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr,
                                           self.mlx.letter_img.img)
        if len(self.mlx.base_letter_map) > 0:
            for _, val in self.mlx.base_letter_map.items():
                if val.img is not None:
                    self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, val.img)
        if len(self.mlx.extended_letter_map) > 0:
            for _, val in self.mlx.extended_letter_map.items():
                if val.img is not None:
                    self.mlx.mlx.mlx_destroy_image(self.mlx.mlx_ptr, val.img)
        if self.mlx.win_ptr is not None:
            self.mlx.mlx.mlx_destroy_window(self.mlx.mlx_ptr, self.mlx.win_ptr)
        if self.mlx.mlx_ptr is not None:
            self.mlx.mlx.mlx_release(self.mlx.mlx_ptr)

    def mymouse(self, button: int, x: int, y: int, mystuff: Any) -> None:
        """Callback for mouse click events.

        Args:
            button (int): The mouse button index pressed.
            x (int): The x-coordinate of the mouse click.
            y (int): The y-coordinate of the mouse click.
            mystuff (Any): User-defined data passed to the hook.
        """
        print(f"Got mouse event! button {button} at {x},{y}.")

    def mykey(self, key_num: int, mlx_var: MlxVar) -> None:
        """Callback for keyboard press events.

        Args:
            key_num (int): The keycode of the key pressed.
            mlx_var (MlxVar): The MLX state container.
        """
        pass
        # print(f"Got key {keynum}, and got my stuff back:")
        # if keynum == 112:
        #     print("Next Move")

    def put_buffer_image(self) -> None:
        """Pushes the current buffer image to the MLX window."""
        if self.mlx.buff_img is not None:
            self.mlx.mlx.mlx_put_image_to_window(
                self.mlx.mlx_ptr, self.mlx.win_ptr, self.mlx.buff_img.img,
                0, 0)
        else:
            print("Error: buffer image is not set")

    @staticmethod
    def set_background(img: ImgData, center: Tuple[int, int],
                       w: int, h: int, color: int = 0xFF000000) -> None:
        """Directly modifies image pixel data to set a background color.

        Uses byte manipulation to fill a rectangular area of the image data
        array.

        Args:
            img (ImgData): The image object containing the data buffer
            to modify.
            center (Tuple[int, int]): (x, y) starting coordinates.
            w (int): Width of the background area to fill.
            h (int): Height of the background area to fill.
            color (int): Hexadecimal color (ARGB) to apply. Defaults to black.
        """
        if w > img.w:
            w = img.w
        if h > img.h:
            h = img.h
        xc, yc = center
        pixel_bytes = color.to_bytes(4, 'little')
        for y in range(yc, yc + h):
            start = y * img.sl + 4 * xc
            end = start + 4 * w
            if img.data is not None:
                img.data[start:end] = pixel_bytes * w

    def rgb_to_hex(self, r: int = 0, g: int = 0, b: int = 0) -> int:
        """Converts RGB components into an ARGB integer.

        Args:
            r (int): Red component (0-255).
            g (int): Green component (0-255).
            b (int): Blue component (0-255).

        Returns:
            int: The 32-bit ARGB hex value.
        """
        return 0xFF000000 | r << 16 | g << 8 | b

    def color_name_to_code(self, color_name: str) -> Any:
        try:
            color_code = name_to_hex(color_name)
            if "#000000" not in color_code:
                return color_code
            else:
                return "#ffffff"
        except ValueError:
            return "#ffffff"
