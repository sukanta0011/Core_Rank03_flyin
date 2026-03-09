from typing import List, Dict, Tuple
from prettytable import PrettyTable
from src.parser.map_constructor import (
    Zone, StartZone, EndZone, ZoneTypes)
from src.parser.parsing_errors import (
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
        self.zone_connection: List[Tuple[str, str]] = []

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
                              [link.target.name for link in val.links]])
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
        start_zone_type: ZoneTypes
        end_zone_type: ZoneTypes

        for hub in hubs:
            if hubs[hub].hub_type.value == "start":
                start = True
                start_x, start_y = hubs[hub].coordinates
                start_zone_type = hubs[hub].zone_type
            if hubs[hub].hub_type.value == "end":
                end = True
                end_x, end_y = hubs[hub].coordinates
                end_zone_type = hubs[hub].zone_type
        if start and end:
            if ((start_x - end_x)**2 + (start_y - end_y)**2) > 0:
                if start_zone_type.value == "blocked":
                    raise MetadataError(
                        "Start zone type can not be blocked")
                if end_zone_type.value == "blocked":
                    raise MetadataError(
                        "End zone type can not be blocked")
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

    def _extract_hub_info(self, line_no: int, line: str) -> None:
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
                        hub_type: str, storage: Dict) -> None:
        if len(hub_info) == 3:
            if "-" in hub_info[0] or " " in hub_info[0]:
                raise HubError(f"HubError: ({line_no}) '-' in hub name is "
                               "not allowed")
            if hub_info[0] in storage.keys():
                raise HubError(f"DuplicateName: ({line_no}), "
                               f"'{hub_info[0]}' already exists.")
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
                # check for duplicate coordinates
                for hub in storage:
                    # print(storage[hub].coordinates)
                    if (x, y) == storage[hub].coordinates:
                        raise CoordinatesError(
                            f"'{line_no}', {hub_info[0]} and "
                            f"{storage[hub].name} has same coordinates")

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

    def _store_hub_metadata(
            self, line_no: int, metadata: List | None,
            hub_name: str, hub_type: str, storage: Dict) -> None:
        # zone = "normal"
        # color = None
        # max_drones = 1
        keys: List = []
        if metadata is not None:
            for info in metadata:
                try:
                    key_val = info.split("=")
                    # Look for missing values
                    if len(key_val) == 1:
                        raise MetadataError(
                            f"({line_no}), '{key_val[0]}' missing '='")
                    elif len(key_val) == 2 and key_val[1].strip() == "":
                        raise MetadataError(
                            f"({line_no}), '{key_val[0]}' missing value")
                    elif len(key_val) > 2:
                        raise MetadataError(
                            f"({line_no}), '{key_val[0]}' value is not "
                            "in proper format")

                    # Check the repetition of the zone metadata
                    if key_val[0] in keys:
                        raise MetadataError(
                            f"({line_no}), {key_val[0]} has duplicate values")
                    else:
                        keys.append(key_val[0])

                    # Extract metadata
                    if key_val[0] == "zone":
                        try:
                            storage[hub_name].update_zone(key_val[1])
                        except Exception:
                            raise MetadataError(
                                f"({line_no}) Unknown zone type '{key_val[1]}'"
                                )
                    elif key_val[0] == "color":
                        color = key_val[1]
                        storage[hub_name].update_color(color)
                    elif key_val[0] == "max_drones":
                        try:
                            drones = int(key_val[1])
                        except ValueError:
                            raise MetadataError(f"({line_no}), '{key_val[0]}' "
                                                "value has to be integer")
                        if drones > 0:
                            if (
                                ("start" in hub_type or "end" in hub_type) and
                                (drones != self.map_dict["drones"])
                               ):
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
                    else:
                        raise MetadataError(f"({line_no}), '{key_val[0]}' "
                                            "is unknown metadata")
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

    def _link_the_connections(self, line_no: int,
                              line: str, storage: Dict) -> None:
        split_line = line.split(":")
        if len(split_line) == 2:
            link_full_data = split_line[1].strip().split("[")
            max_link_capacity = 1
            if len(link_full_data) == 2:
                max_link_capacity = self._extract_max_link_capacity(
                    line_no, link_full_data[1])
            links = link_full_data[0].strip().split("-")
            # Checking for proper linking
            if len(links) == 1:
                raise LinkingError(
                    f"LinkError: ({line_no}), '{links[0]}' missing connection")
            elif len(links) == 2 and links[1].strip() == "":
                raise LinkingError(
                    f"LinkError: ({line_no}), '{links[0]}' missing "
                    "connecting link")
            elif len(links) > 2:
                raise LinkingError(
                    f"LinkError: ({line_no}), '{links[0]}' value is not "
                    "in proper format")

            hub1 = links[0].strip()
            hub2 = links[1].strip()
            stored_hubs = list(storage.keys())
            if hub1 in stored_hubs and hub2 in stored_hubs:
                # hub1_idx = stored_hubs.index(hub1)
                # hub2_idx = stored_hubs.index(hub2)
                # print(hub1_idx, hub2_idx)
                if ((hub1, hub2) in self.zone_connection or
                        (hub2, hub1) in self.zone_connection):
                    raise LinkingError(
                        f"LinkError: ({line_no}), connection {hub1}-{hub2}"
                        " already exists"
                        )
                else:
                    self.zone_connection.append((hub1, hub2))
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
            if link_capacity[0] != "max_link_capacity":
                raise MaxLinkError(
                    f"MaxLinkError: ({line_no}), '{link_capacity[0]}' "
                    "unknown link capacity info"
                )
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
    # file_path = "maps/my_maps/priority_map1.txt"
    # file_path = "maps/easy/02_simple_fork.txt"
    # file_path = "maps/medium/03_priority_puzzle.txt"
    # file_path = "maps/medium/01_dead_end_trap.txt"
    # file_path = "maps/medium/02_circular_loop.txt"
    # file_path = "maps/hard/01_maze_nightmare.txt"
    # file_path = "maps/challenger/01_the_impossible_dream.txt"
    file_path = "invalid_maps/map20.txt"
    map_parser = MapParser()
    map_parser.parse(file_path)
    map_parser.show_map()
    map = map_parser.get_map()
    # DFS_algo(map)
