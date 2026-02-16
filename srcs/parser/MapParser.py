from typing import List, Dict
from prettytable import PrettyTable
from srcs.parser.GraphConstructor import Zone, StartZone, EndZone
from srcs.parser.ParsingErrors import (
    MapError,
    DroneNumError,
    FormattingError,
    HubError,
    CoordinatesError,
    MetadataError,
    DroneOccupancyError,
    LinkingError,
    MaxLinkError
)


class MapParser:
    def __init__(self) -> None:
        self.map_dict: Dict = {}

    def parse(self, path: str) -> None:
        error_encountered = True
        drone = 0
        hubs = 0
        connections = 0
        try:
            with open(path, "r") as fl:
                for i, line in enumerate(fl.readlines()):
                    if line.startswith("#") or line.startswith("\n"):
                        pass
                    elif line.startswith("nb_drones"):
                        drone += 1
                        self._extract_drone_counts(i + 1, line)
                    elif line.startswith("hub") or\
                        line.startswith("start_hub") or\
                            line.startswith("end_hub"):
                        hubs += 1
                        self._extract_hub_info(i + 1, line)
                    elif line.startswith("connection"):
                        connections += 1
                        storage = self.map_dict.get('hubs')
                        if storage is not None:
                            self._link_the_connections(i + 1, line, storage)
                        else:
                            raise MapError(
                                "MapError: Map to store the hubs info "
                                "before checking the connections")
                    else:
                        raise FormattingError(
                            f"MapError: ({i + 1}) unknown line starting")
            if drone == 1 and hubs > 1 and connections > 0:
                if self.has_proper_start_end(self.map_dict['hubs']):
                    error_encountered = False
            else:
                raise MapError(
                    f"MapError: Map '{path}' do not have complete information")

        except FileNotFoundError:
            print(f"ParsingError: invalid path '{path}'")
        except PermissionError:
            print(f"ParsingError: file '{path}' do not have "
                  "reading permission")
        except MapError as e:
            print(f"ParsingError->{e}")
        except Exception as e:
            print(f"GeneralError: {e}")
        if error_encountered:
            self.reset_map()

    def get_drone_num(self) -> int | None:
        return self.map_dict.get("drones")

    def get_map(self) -> Dict[str, Zone] | None:
        return self.map_dict.get("hubs")

    def show_map(self) -> None:
        try:
            hubs = self.map_dict.get("hubs")
            if hubs is not None:
                t = PrettyTable(["Name", "Type", "Coordinates", "Zone",
                                "Color", "Capacity", "links"])
                for key, val in hubs.items():
                    t.add_row([key, val.hub_type.value, val.coordinates,
                              val.zone_type.value, val.color, val.capacity,
                              [(link.target.name, link.link_capacity)
                               for link in val.links]])
                print(t)
        except Exception as e:
            print(f"TableGenerationError: {e}")

    def reset_map(self) -> None:
        self.map_dict = {}

    def has_proper_start_end(self, hubs: Dict) -> bool:
        start = False
        end = False
        start_x, start_y = 0, 0
        end_x, end_y = 0, 0
        for hub in hubs:
            if hubs[hub].hub_type.value == "start":
                start = True
                start_x, start_y = hubs[hub].coordinates
            if hubs[hub].hub_type.value == "end":
                end = True
                end_x, end_y = hubs[hub].coordinates
        if start and end:
            if ((start_x - end_x)**2 + (start_y - end_y)**2) > 0:
                return True
            else:
                raise MapError(
                    "MapError: start and end has same coordinates")
        else:
            raise MapError(
                "MapError: Map do not have both start and end hub info")

    def _extract_drone_counts(self, line_no: int, line: str) -> None:
        split_line = line.split("\n")[0].split(":")
        if len(split_line) == 2:
            try:
                drones_num = int(split_line[1])
            except ValueError:
                raise DroneNumError(f"DroneError: line no ({line_no}) "
                                    "Drone number has to be integer")
            if drones_num > 0:
                self.map_dict["drones"] = drones_num
            else:
                raise DroneNumError(f"DroneError: line no ({line_no}) "
                                    "Drone number has to be positive "
                                    "integer")
        else:
            raise FormattingError(f"DroneError: line no ({line_no}) "
                                  "is in wrong format")

    def _extract_hub_info(self, line_no: int, line: str):
        split_line = line.split("\n")[0].split(":")
        if len(split_line) == 2:
            if "hubs" not in self.map_dict.keys():
                self.map_dict["hubs"] = {}
            hub_info = split_line[1].strip().split("[")
            hub_info_list = hub_info[0].strip().split(" ")
            if len(hub_info) == 2:
                metadata_list = hub_info[1].strip()[: -1].split(" ")
            else:
                metadata_list = None
            try:
                self._store_hub_info(line_no, hub_info_list,
                                     split_line[0], self.map_dict["hubs"])
                self._store_hub_metadata(line_no, metadata_list,
                                         hub_info_list[0], split_line[0],
                                         self.map_dict["hubs"])
            except HubError as e:
                raise HubError(f"HubError->{e}")
        else:
            raise FormattingError(f"HubError: ({line_no}) "
                                  "is in wrong format")

    def _store_hub_info(self, line_no: int, hub_info: List,
                        hub_type: str, storage: Dict):
        if len(hub_info) == 3:
            if "-" in hub_info[0]:
                raise HubError(f"HubError: ({line_no}) '-' in hub name is "
                               "not allowed")
            if hub_info[0] in storage.keys():
                pass
            else:
                try:
                    x = int(hub_info[1])
                    y = int(hub_info[2])
                except ValueError:
                    raise CoordinatesError(f"CoordinateError: ({line_no})"
                                           " Hub coordinates need to be "
                                           "integers")
                if x < 0:
                    raise CoordinatesError(f"CoordinateError: ({line_no})"
                                           " Hub x coordinates need to be "
                                           "positive integer")
                if "start" in hub_type:
                    storage[hub_info[0]] = StartZone(
                        name=hub_info[0], x=x, y=y,
                        total_drones=self.map_dict['drones'])
                elif "end" in hub_type:
                    storage[hub_info[0]] = EndZone(
                        name=hub_info[0], x=x, y=y,
                        total_drones=self.map_dict['drones'])
                else:
                    storage[hub_info[0]] = Zone(
                        name=hub_info[0], x=x, y=y,)
        else:
            raise FormattingError(f"HubError: ({line_no}) "
                                  "do not have require hub infos")

    def _store_hub_metadata(self, line_no: int, metadata: List | None,
                            hub_name: str, hub_type: str, storage: Dict):
        # zone = "normal"
        # color = None
        # max_drones = 1
        if metadata is not None:
            for info in metadata:
                try:
                    key_val = info.split("=")
                    if key_val[0] == "zone":
                        zone = key_val[1]
                        storage[hub_name].update_zone(zone)
                    if key_val[0] == "color":
                        color = key_val[1]
                        storage[hub_name].update_color(color)
                    if key_val[0] == "max_drones":
                        drones = int(key_val[1])
                        if drones > 0:
                            if ("start" in hub_type or "end" in hub_type) and\
                                drones != self.map_dict["drones"]:
                                raise DroneOccupancyError(
                                    f"DroneOccupancyError: ({line_no}) "
                                    f"Max_drone({drones}) in {hub_type} has "
                                    f"to be equal to {self.map_dict['drones']}"
                                    )
                            storage[hub_name].update_capacity(drones)
                        else:
                            raise DroneOccupancyError(
                                f"DroneOccupancyError: ({line_no}) "
                                f"'{key_val[0]}' has to be positive")
                except IndexError:
                    raise MetadataError(f"MetadataError: ({line_no}) "
                                        f"metadata {info} is not properly "
                                        "formatted")
                except MetadataError as e:
                    raise MetadataError(f"MetadataError->{e}")
        # storage[hub_name].update({
        #     "zone": zone,
        #     "color": color,
        #     "max_drones": max_drones,
        # })

    def _link_the_connections(self, line_no: int, line: str, storage: Dict):
        split_line = line.split(":")
        if len(split_line) == 2:
            link_full_data = split_line[1].strip().split("[")
            max_link_capacity = 1
            if len(link_full_data) == 2:
                max_link_capacity = self._extract_max_link_capacity(
                    line_no, link_full_data[1])
            links = link_full_data[0].strip().split("-")
            hub1 = links[0].strip()
            hub2 = links[1].strip()
            if hub1 in storage.keys() and hub2 in storage.keys():
                storage[hub1].add_link(storage[hub2], max_link_capacity)
                # storage[hub2].add_link(storage[hub1], max_link_capacity)
            else:
                raise LinkingError(
                    f"LinkError: ({line_no}) link name {hub1}, {hub2} does "
                    f"not exists in hub names {storage.keys()} ")
        else:
            raise LinkingError(
                f"LinkingError: ({line_no}) has improper formatting")

    def _extract_max_link_capacity(self, line_no: int, metadata: str) -> int:
        link_capacity = metadata[: -1].split("=")
        if len(link_capacity) == 2:
            try:
                max_link = int(link_capacity[1].strip())
                if max_link > 0:
                    return max_link
                else:
                    raise MaxLinkError(
                        f"MaxLinkError: ({line_no}) {link_capacity[0]} "
                        "has to be positive")
            except ValueError:
                raise MaxLinkError(
                    f"MaxLinkError: ({line_no}) {link_capacity[0]} has "
                    "to be integer")
        else:
            raise MaxLinkError(
                f"MaxLinkError: ({line_no}) {link_capacity[0]} "
                "has wrong formatting")


if __name__ == "__main__":
    file_path = "maps/easy/02_simple_fork.txt"
    # file_path = "maps/medium/01_dead_end_trap.txt"
    # file_path = "maps/medium/02_circular_loop.txt"
    # file_path = "maps/hard/01_maze_nightmare.txt"
    # file_path = "maps/challenger/01_the_impossible_dream.txt"
    # file_path = "maps/invalid/map1.txt"
    map_parser = MapParser()
    map_parser.parse(file_path)
    map_parser.show_map()
    map = map_parser.get_map()
    # DFS_algo(map)
