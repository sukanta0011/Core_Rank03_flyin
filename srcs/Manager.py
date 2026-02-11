from typing import List, Dict
from srcs.GraphVisualizer import GraphVisualizer
from srcs.Simulator import Simulator


class SimulatorManager:
    pass


class VisualSimulationManager:
    def __init__(self, simulator: Simulator, visualizer: GraphVisualizer,
                 valid_paths: Dict[str, List]):
        self.simulator = simulator
        self.visualizer = visualizer
        self.valid_paths = valid_paths

    def play(self):
        self.visualizer.generate_map(self.valid_paths)
        for i in range(4):
            self.simulator.next_move(self.valid_paths)
            self.visualizer.generate_map(self.valid_paths)
