from __future__ import annotations
from typing import Dict, List, Tuple, Callable, TYPE_CHECKING
import math
from src.simulator.simulation_engine import Drone
from src.parser.map_constructor import Zone
from src.simulator.helpers import get_pos_obj
from .mlx_tools.base_mlx import MlxVar
from .mlx_tools.image_operations import ImageOperations
if TYPE_CHECKING:
    from src.visualizer.map_visualizer import ConstantParameters


def drone_animation_translation(
        params: Tuple[MlxVar, ConstantParameters,
                      List[Drone], Dict[str, Zone],
                      Callable, Callable, Callable,
                      Callable, Callable,
                      Callable, Callable]) -> None:
    mlx_var, const, drones, zones, \
        func_move, func_txt, \
        func_throughput, func_cost, \
        ani_counter, update, auto_animate = params
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    if mlx_var.static_bg.data is not None and \
       mlx_var.buff_img.data is not None:
        mlx_var.buff_img.data[:] = mlx_var.static_bg.data[:]
    counter = ani_counter()
    all_drone_moved = True
    drone_info = ""
    for no, drone in enumerate(drones):
        xf, yf = drone.target_pos
        xi, yi = drone.last_pos
        xc, yc = drone.current_pos
        drone.moving = False
        distance = (yf - yc)**2 + (xf - xc)**2
        # print(xi, yi, xf, yf, xc, yc, xc >= xf, yc >= yf)
        if distance > 0.0025:
            all_drone_moved = False
            drone.moving = True
            if xf - xi == 0:
                yc += (yf - yi) * const.fractional_move
            elif yf - yi == 0:
                xc += (xf - xi) * const.fractional_move
            else:
                slope = (yf - yi) / (xf - xi)
                xc += (xf - xi) * const.fractional_move
                yc = slope * (xc - xi) + yi
        else:
            xc, yc = float(xf), float(yf)
        if len(drone.txt) > 0:
            drone_info += f"{drone.txt} "
        drone.current_pos = [xc, yc]
        xc_scaled = int(xc * const.mul + const.x_offset)
        yc_scaled = int(yc * const.mul + const.y_cent +
                        10 * math.sin(no + 3.14 * counter / 180))

        ImageOperations.copy_img(
            mlx_var.buff_img, mlx_var.drone_img,
            (xc_scaled - mlx_var.drone_img.w // 2,
             yc_scaled - mlx_var.drone_img.h // 2))
        func_txt(mlx_var, mlx_var.buff_img,
                 (xc_scaled - mlx_var.drone_img.w // 2,
                  yc_scaled - mlx_var.drone_img.h), drone.name, " ", 0.3)
    func_move(mlx_var, mlx_var.buff_img, (10, 180), "", "_",
              0.4, 0xFF000000, 0xff2ebdca)
    func_throughput(mlx_var, mlx_var.buff_img, (520, 100), "", "_",
                    0.35, 0xFF00FFFF)
    func_cost(mlx_var, mlx_var.buff_img, (520, 200), "", "_",
              0.35, 0xFF00FFFF)

    if len(drone_info) > 0:
        func_txt(mlx_var, mlx_var.buff_img, (10, 210), drone_info, " ", 0.5)
    for _, zone in zones.items():
        coord = zone.coordinates
        xi = coord[0] * const.mul + const.x_offset
        yi = coord[1] * const.mul + const.y_cent
        func_txt(mlx_var, mlx_var.buff_img,
                 (xi - const.sq_len, yi - const.sq_len),
                 f"{zone.capacity}:{zone.occupancy}", " ", 0.4)
    # print([drone.name for drone in drones])
    # copy_img_to_buffer(mlx_var.buff_img, mlx_var.static_bg, (0, 0))
    # print(f"Animation updated: "
    #       f"{[(drone.name, drone.target_pos) for drone in drones]}")
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)
    if all_drone_moved and auto_animate():
        end = get_pos_obj(zones, "end")
        if end is not None and (end.occupancy < len(drones)):
            update()


# def drone_animation_hovering(params: Tuple[MlxVar, str]):
#     mlx_var = params[0]
#     print(f"test: {params[1]}")
#     mlx_var.animation_counter += 1
#     time.sleep(0.1)
#     y = 100 + int(math.sin(mlx_var.animation_counter) * 4)
#     # mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
#     set_buffer_image_background(mlx_var.buff_img, 400, 600)
#     copy_img_to_buffer(mlx_var.buff_img, mlx_var.drone_img, (100, y))
#     mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
#                                         mlx_var.buff_img.img, 0, 0)
