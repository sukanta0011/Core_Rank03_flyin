from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import math
from srcs.simulator.Simulator import Drone
from srcs.parser.GraphConstructor import Zone
from srcs.mlx_tools.BaseMLX import MlxVar
from srcs.mlx_tools.ImageOperations import copy_img
if TYPE_CHECKING:
    from srcs.visualizer.GraphVisualizer import ConstantParameters


def drone_animation_translation(
        params: Tuple[MlxVar, ConstantParameters,
                      List[Drone], Dict[str, Zone]]):
    mlx_var, const, drones, zones, func_move, func_txt = params
    mlx_var.mlx.mlx_clear_window(mlx_var.mlx_ptr, mlx_var.win_ptr)
    mlx_var.buff_img.data[:] = mlx_var.static_bg.data[:]

    all_drone_moved = True
    drone_info = ""
    # time.sleep(0.01)
    for drone in drones:
        xf, yf = drone.target_pos
        xi, yi = drone.last_pos
        xc, yc = drone.current_pos
        distance = math.sqrt((yf - yc)**2 + (xf - xc)**2)
        # print(xi, yi, xf, yf, xc, yc, xc >= xf, yc >= yf)
        if distance > 0.05:
            all_drone_moved = False
            if xf - xi == 0:
                # print("Vertical")
                yc += (yf - yi) * const.fractional_move
            elif yf - yi == 0:
                # print("horizontal")
                xc += (xf - xi) * const.fractional_move
            else:
                slope = (yf - yi) / (xf - xi)
                xc += (xf - xi) * const.fractional_move
                # print(f"Angle: {slope}")
                yc = slope * (xc - xi) + yi
        else:
            xc, yc = float(xf), float(yf)
        if len(drone.txt) > 0:
            drone_info += f"{drone.txt} "
        drone.current_pos = [xc, yc]
        xc_scaled = int(xc * const.mul + const.x_offset)
        yc_scaled = int(yc * const.mul + mlx_var.buff_img.h // 2)

        copy_img(mlx_var.buff_img, mlx_var.drone_img,
                           (xc_scaled - mlx_var.drone_img.w // 2,
                            yc_scaled - mlx_var.drone_img.h // 2))
        func_txt(mlx_var, mlx_var.buff_img, (xc_scaled - mlx_var.drone_img.w // 2,
             yc_scaled - mlx_var.drone_img.h), drone.name, " ", 0.3)
    func_move(mlx_var, mlx_var.buff_img, (50, 210), "", "_",
              0.5, 0xFF00FF00)
    if len(drone_info) > 0:
        func_txt(mlx_var, mlx_var.buff_img, (50, 250), drone_info, " ", 0.4)
    for _, zone in zones.items():
        coord = zone.coordinates
        xi = coord[0] * const.mul + const.x_offset
        yi = coord[1] * const.mul + mlx_var.buff_img.h // 2
        func_txt(mlx_var, mlx_var.buff_img,
                 (xi - 40, yi - 45), f"{zone.capacity}:{zone.occupancy}", " ", 0.4)
    # print([drone.name for drone in drones])
    # copy_img_to_buffer(mlx_var.buff_img, mlx_var.static_bg, (0, 0))
    # print(f"Animation updated: {[(drone.name, drone.target_pos)for drone in drones]}")
    mlx_var.mlx.mlx_put_image_to_window(mlx_var.mlx_ptr, mlx_var.win_ptr,
                                        mlx_var.buff_img.img, 0, 0)
    if all_drone_moved:
        pass


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