from __future__ import annotations
from typing import List, Tuple, Protocol, Dict, TYPE_CHECKING
from .mlx_errors import (
    ImgError,
    ParametersError,
    InitializationError,
    OperationError
)
if TYPE_CHECKING:
    from .base_mlx import MlxVar


class ImgData:
    """Container for MiniLibX image metadata and pixel data.

    This structure mimics the underlying C struct used by MLX to handle
    image buffers and their properties.

    Attributes:
        img (Any): The pointer to the MLX image object.
        w (int): Image width in pixels.
        h (int): Image height in pixels.
        data (memoryview | bytearray): The raw pixel data buffer.
        sl (int): Size line (number of bytes per horizontal line).
        bpp (int): Bits per pixel (color depth).
        iformat (int): Endianness format of the pixel data.
    """
    def __init__(self) -> None:
        self.img = None
        self.w = 0
        self.h = 0
        self.data = None
        self.sl = 0  # size line
        self.bpp = 0  # bits per pixel
        self.iformat = 0


class ImageOperations:
    """Static utility class for low-level image manipulation and
    allocation via MLX.

    This class provides core graphical operations, abstracting the complexity
    of raw memory buffer manipulation and MLX-specific pointer management.
    """
    @staticmethod
    def generate_blank_image(mlx: MlxVar, w: int, h: int) -> ImgData:
        """Allocates a new empty image buffer using the MLX library.

        Args:
            mlx (MlxVar): The MLX state container providing the MLX
            pointer and engine.
            w (int): Target width of the image in pixels.
            h (int): Target height of the image in pixels.

        Returns:
            ImgData: An initialized container holding the image pointer and its
                corresponding raw data address.

        Raises:
            ParametersError: If dimensions are non-positive or non-integers.
            InitializationError: If the MLX engine fails to allocate the image.
        """
        if w <= 0 or h <= 0:
            raise ParametersError(
                "ParametersError: Blank image generation failed"
                f"w and h has to be positive ({w}, {h})")
        if not isinstance(w, int) or not isinstance(h, int):
            raise ParametersError(
                "Blank image generation failed"
                f"w and h has to be integer ({w}, {h})")
        new_img = ImgData()
        new_img.h = int(h)
        new_img.w = int(w)
        try:
            new_img.img = mlx.mlx.mlx_new_image(
                mlx.mlx_ptr, new_img.w, new_img.h)
            new_img.data, new_img.bpp, new_img.sl, new_img.iformat = \
                mlx.mlx.mlx_get_data_addr(new_img.img)
            return new_img
        except Exception as e:
            raise InitializationError(
                f"Blank image generation failed: {e}"
            )

    @staticmethod
    def xmp_to_img(mlx: MlxVar, image_loc: str) -> ImgData:
        """Loads an XPM file from disk and initializes an ImgData container.

        Args:
            mlx (MlxVar): The MLX state container.
            image_loc (str): Path to the .xpm file.

        Returns:
            ImgData: The container populated with loaded image data
            and dimensions.

        Raises:
            InitializationError: If the file is inaccessible or format
            is invalid.
        """
        try:
            img = ImgData()
            result = mlx.mlx.mlx_xpm_file_to_image(mlx.mlx_ptr, image_loc)
            img.img, img.w, img.h = result
            img.data, img.bpp, img.sl, img.iformat = \
                mlx.mlx.mlx_get_data_addr(img.img)
            return img
        except Exception as e:
            raise InitializationError(
                f"Unable to load xmp image {image_loc}. {e}"
            )

    @staticmethod
    def copy_img(dest: ImgData, src: ImgData, center: Tuple[int, int]) -> None:
        """Copies pixel data from a source image into a destination image.

        Performs boundary checking to ensure the source fits within the
        destination. Copies are performed via efficient memory slicing.

        Args:
            dest (ImgData): The target image buffer to modify.
            src (ImgData): The source image buffer to copy from.
            center (Tuple[int, int]): The (x, y) top-left starting position
                in the destination.

        Raises:
            ParametersError: If coordinates are invalid or source exceeds
            destination.
            OperationError: If image data buffers are uninitialized.
        """
        start_x, start_y = center
        if not isinstance(start_x, int) or not isinstance(start_y, int):
            raise ParametersError(
                "Copying image failed, center coordinate need to be "
                f"integer ({center})")
        if (0 <= start_x < dest.w) and (0 <= start_y < dest.h):
            if start_x + src.w > dest.w:
                w = dest.w - start_x
                sl = w
            else:
                w = src.w
                sl = src.sl
            if start_y + src.h > dest.h:
                h = dest.h - start_y
            else:
                h = src.h
        else:
            raise ParametersError(
                "(fn :ImageOperations.copy_img) "
                "Source image dimension is bigger than destination image")
        for y in range(h):
            dest_start = (start_y + y) * dest.sl + (4 * start_x)
            dest_end = dest_start + (4 * w)
            src_start = y * sl
            src_end = src_start + (w * 4)
            if dest.data is not None and src.data is not None:
                dest.data[dest_start:dest_end] = src.data[src_start:src_end]
            else:
                raise OperationError(
                    "Cropping failed, The dest or src image is empty"
                )

    @staticmethod
    def crop_img(dest: ImgData, src: ImgData, center: Tuple[int, int]) -> None:
        """Fills a destination image by cropping a portion of a source image.

        Unlike copy_img, this fills the entire 'dest' buffer starting from
        the 'center' point of the 'src'.

        Args:
            dest (ImgData): The smaller target buffer to fill.
            src (ImgData): The larger source buffer to crop from.
            center (Tuple[int, int]): The (x, y) top-left starting position
                within the source.

        Raises:
            ParametersError: If center coordinates are out of bounds.
            OperationError: If buffers are missing.
        """
        start_x, start_y = center
        if not isinstance(start_x, int) or not isinstance(start_y, int):
            raise ParametersError(
                "Cropping image failed, center coordinate need to be "
                f"integer ({center})")
        if (0 <= start_x < src.w) and (0 <= start_y < src.h):
            if start_x + dest.w > src.w:
                w = src.w - start_x
                sl = w
            else:
                w = dest.w
                sl = dest.sl
            if start_y + dest.h > src.h:
                h = src.h - start_y
            else:
                h = dest.h
        else:
            raise ParametersError(
                "Source image dimension is bigger than destination image")
        for y in range(h):
            dest_start = y * sl
            dest_end = dest_start + (4 * w)
            src_start = (start_y + y) * src.sl + (4 * start_x)
            src_end = src_start + (4 * w)
            if dest.data is not None and src.data is not None:
                dest.data[dest_start:dest_end] = src.data[src_start:src_end]
            else:
                raise OperationError(
                    "Cropping failed, The dest or src image is empty"
                )

    @staticmethod
    def set_pixel(img: ImgData, center: int | Tuple[int, int],
                  color: int = 0xFFFFFFFF) -> None:
        """Directly modifies a specific pixel in the image memory buffer.

        Supports both direct index-based access and (x, y) coordinate mapping.

        Args:
            img (ImgData): The image buffer to modify.
            center (int | Tuple[int, int]): Either a direct byte offset (int)
                or a coordinate pair (tuple).
            color (int): Hexadecimal color value (ARGB) in
            little-endian format.

        Raises:
            ParametersError: If the pixel location is outside the
            allocated memory.
            OperationError: If the underlying memoryview is inaccessible.
        """
        if isinstance(center, int):
            # print(f"one position: {center}")
            pos = center
            if pos >= (img.w * img.h * 4) or pos < 0:
                raise ParametersError(
                    f"Unable to set pixel, {pos}, is out of range of "
                    "the image dimensions"
                )
        elif isinstance(center, tuple):
            if len(center) == 2:
                x, y = center
                if not isinstance(x, int) or not isinstance(y, int):
                    raise ParametersError(
                        "Setting failed, center coordinate need to be "
                        f"integer ({center})")
                if x < 0 or x > img.w or y < 0 or y > img.h:
                    raise ParametersError(
                        f"Pixel position outside image range, x:{x}, y: {y}")
                pos = (y * img.sl) + (x * (img.bpp // 8))  # Color is 8 bits
            else:
                raise ParametersError(f"Invalid center format {center}. "
                                      "Allowed (x, y)")
        else:
            raise ParametersError(f"Error: Invalid center instance {center}. "
                                  "Allowed instances are int/tuple")

        try:
            if img.data is not None:
                img.data[pos: pos + 4] = (color).to_bytes(4, 'little')
        except Exception as e:
            raise OperationError(f"Unable to set pixel: {e}")


class Stages(Protocol):
    """Structural protocol defining a processing stage for image data.

    Any class implementing a `process` method with this signature can be
    added to the TxtToImage pipeline (e.g., scalers, color changers).
    """
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color: int = 0xFFFFFFFF,
                bg_color: int = 0x00000000) -> ImgData:
        """Processes the input image and returns a modified version.

        Args:
            mlx: The MLX state container.
            img: The source image to process.
            factor: Scaling multiplier.
            font_color: Target hexadecimal color for the foreground.
            bg_color: Target hexadecimal color for the background.

        Returns:
            ImgData: The newly processed image.
        """
        pass


class ImageScaler:
    """A processing stage that resizes images using nearest-neighbor
    interpolation."""
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color: int = 0xFFFFFFFF,
                bg_color: int = 0x00000000) -> ImgData:
        """Scales the source image by a given factor.

        Args:
            mlx: The MLX state container.
            img: The source image data.
            factor: The scale factor (must be > 0).
            font_color: Unused in this stage.
            bg_color: Unused in this stage.

        Returns:
            ImgData: A new, resized image buffer.

        Raises:
            ParametersError: If the scale factor is non-positive.
            ImgError: If blank image generation fails.
            OperationError: If source data is missing.
        """
        if factor <= 0:
            raise ParametersError(
                "Image scaling failed, Factor has to be "
                f"bigger than 0, not {factor}")
        try:
            new_img = ImageOperations.generate_blank_image(
                mlx, int(img.w * factor), int(img.h * factor))
        except ImgError as e:
            raise ImgError(f"{type(e).__name__}: {e}")

        for y in range(new_img.h):
            for x in range(new_img.w):
                new_img_pos = y * new_img.sl + (4 * x)
                img_pos = int(y / factor) * img.sl + \
                    (4 * int(x / factor))
                if new_img.data is not None and img.data is not None:
                    new_img.data[new_img_pos: new_img_pos + 4] = \
                        img.data[img_pos: img_pos + 4]
                else:
                    raise OperationError(
                        "Cropping failed, The dest or src image is empty"
                        )
        return new_img


class TxtColorChanger:
    """A processing stage that rebinds colors for font glyphs."""
    def process(self, mlx: MlxVar, img: ImgData,
                factor: float = 1.0, font_color: int = 0xFFFFFFFF,
                bg_color: int = 0x00000000) -> ImgData:
        """Changes the font and background colors of a glyph.

        Identifies 'empty' pixels (black) and replaces them with bg_color,
        while replacing non-black pixels with font_color.

        Args:
            mlx: The MLX state container.
            img: The source glyph image.
            factor: Unused in this stage.
            font_color: The new foreground color (ARGB).
            bg_color: The new background color (ARGB).

        Returns:
            ImgData: A new image buffer with updated color values.
        """
        try:
            new_img = ImageOperations.generate_blank_image(mlx, img.w, img.h)
        except ImgError as e:
            raise ImgError(f"{type(e).__name__}: {e}")

        try:
            for i in range(0, new_img.h * new_img.w * 4, 4):
                if img.data is not None and new_img.data is not None:
                    if img.data[i + 1] == 0 and img.data[i + 2] == 0 and \
                            img.data[i + 3] == 0:
                        new_img.data[i: i + 4] = \
                            (bg_color).to_bytes(4, "little")
                    else:
                        new_img.data[i: i + 4] = (font_color).to_bytes(
                            4, "little")
            return new_img
        except Exception as e:
            raise OperationError(
                f"Unable to change letter colour: {e}"
            )


class TxtToImage:
    """Handles rendering of text strings into graphical buffers with caching.

    Uses a pipeline of 'Stages' to transform base character glyphs into
    styled versions (scaled, colored, etc.) and maintains a cache to
    minimize redundant processing.

    Attributes:
        base_letter_map (Dict[str, ImgData]): Original source glyphs.
        extended_letter_map (Dict[str, ImgData]): Cache of processed glyphs,
            keyed by character and style parameters.
        stages (List[Stages]): Ordered list of transformations to apply.
    """
    def __init__(self, base_letter_map: Dict[str, ImgData],
                 extended_letter_dict: Dict[str, ImgData]) -> None:
        """Initializes the text renderer with a base glyph set."""
        self.stages: List[Stages] = []
        self.base_letter_map = base_letter_map
        self.extended_letter_map: Dict[str, ImgData] = extended_letter_dict

    def add_stages(self, stage: Stages) -> None:
        """Appends a processing stage to the rendering pipeline."""
        self.stages.append(stage)

    def print_txt(self, mlx: MlxVar, buff_img: ImgData, txt: str,
                  origin: Tuple[int, int], factor: float = 1.0,
                  font_color: int = 0xFFFFFFFF,
                  bg_color: int = 0x00000000) -> int:
        """Renders a string into a target image buffer.

        Each character is retrieved from cache or processed through the stages
        if not yet cached. The characters are then blitted sequentially.

        Args:
            mlx: The MLX state container.
            buff_img: The destination image to draw upon.
            txt: The string to render.
            origin: The (x, y) coordinates for the start of the text.
            factor: Scaling factor for the text.
            font_color: Color of the characters.
            bg_color: Background color of the character bounding boxes.

        Returns:
            int: The resulting x-coordinate after the last character.

        Raises:
            OperationError: If rendering fails for any character in the string.
        """
        x, y = origin
        for letter in txt:
            try:
                comb_key = f"{letter}_{factor}_{font_color}_{bg_color}"
                img = self.extended_letter_map.get(comb_key)
                if img is None:
                    try:
                        img = self.base_letter_map[letter]
                    except KeyError:
                        img = self.base_letter_map[" "]
                    for stage in self.stages:
                        img = stage.process(mlx, img, factor, font_color,
                                            bg_color)
                    if img is not None:
                        self.extended_letter_map[comb_key] = img
                ImageOperations.copy_img(buff_img, img, (x, y))
                x += img.w
            except Exception as e:
                raise OperationError(
                    f"Unable to print '{letter}'-> {type(e).__name__}: {e}"
                )
        return x


# def tester():
#     from srcs.mlx_tools.LetterToImageMapper import LetterToImageMapper
#     from srcs.mlx_tools.BaseMLX import MyMLX
#     try:
#         mlx = MyMLX(1000, 800)
#         # image = "images/alphabets.xpm"
#         letter_map = LetterToImageMapper(mlx.mlx)
#         # copy_img_to_buffer(mlx.mlx.buff_img, mlx.mlx.letter_img, (0, 0))
#         letter_map.create_map()
#         ImageOperations.copy_img(
#             mlx.mlx.buff_img, mlx.mlx.base_letter_map["A"], (0, 0))
#         ImageOperations.copy_img(
#             mlx.mlx.buff_img, mlx.mlx.base_letter_map["e"], (50, 0))
#         ImageOperations.copy_img(
#             mlx.mlx.buff_img, mlx.mlx.base_letter_map["1"], (150, 0))
#         ImageOperations.copy_img(
#             mlx.mlx.buff_img, mlx.mlx.base_letter_map["("], (100, 0))
#         ImageOperations.copy_img(
#             mlx.mlx.buff_img, mlx.mlx.base_letter_map[")"], (200, 0))
#         scaler = ImageScaler()
#         scaled_a = scaler.process(mlx.mlx, mlx.mlx.base_letter_map["A"], 0.5)
#         ImageOperations.copy_img(mlx.mlx.buff_img, scaled_a, (250, 0))

#         letter_color = TxtColorChanger()
#         colored_a = letter_color.process(mlx.mlx,
#                       mlx.mlx.base_letter_map["A"])

#         txt_to_img = TxtToImage(mlx.mlx.base_letter_map,
#                                 mlx.mlx.extended_letter_map)
#         txt_to_img.add_stages(scaler)
#         txt_to_img.add_stages(letter_color)
#         txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img,
#                              "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
#                              (0, 180), 0.5)
#         txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img,
#                              "abcdefghijklmnopqrstuvwxyz",
#                              (0, 260))
#         txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img,
#                              "0123456789",
#                              (0, 340))
#         txt_to_img.print_txt(mlx.mlx, mlx.mlx.buff_img,
#                              ".,;:_#'!\"/?<>%&*()",
#                              (0, 420))

#         ImageOperations.copy_img(mlx.mlx.buff_img, colored_a, (300, 0))

#         mlx.mlx.mlx.mlx_put_image_to_window(
#             mlx.mlx.mlx_ptr, mlx.mlx.win_ptr, mlx.mlx.buff_img.img, 0, 0)
#         mlx.start_mlx()
#     except Exception as e:
#         print(f"{type(e).__name__}: {e}")


# if __name__ == "__main__":
#     tester()
