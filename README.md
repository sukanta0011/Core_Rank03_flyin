**This project has been created as part of the 42 curriculum by sudas**
# FLYIN

### Description:
FLYIN is a discrete-event simulation designed to optimize drone swarm throughput across complex, constraint-heavy directed graphs. The project implements a custom resource-reservation algorithm to manage concurrent movement, ensuring no capacity overflows while maximizing the flow of agents from start to goal.

#### Features
- Concurrent Flow Management: Handles multi-agent pathfinding with strict hub and link capacity constraints.
- Priority-Aware Routing: Intelligently prioritizes specialized paths (e.g., Restricted or Priority zones) without compromising global throughput.
- Real-Time MLX Visualization: A custom-built graphical engine using MiniLibX, featuring:
  - Double-Buffered Rendering: Smooth, flicker-free 60 FPS animations.
  - State Monitoring: Real-time display of hub occupancy and individual drone progress.
  - Dynamic Animations: Procedural hovering effects and linear interpolation (LERP) for movement.
- Interactive Controls:
 - 1: Step-by-step manual simulation.
 - 2: Fully automated real-time animation.
 - 3: Pause simulation.
 - 4: Terminate visualizer.

## Introduction:
Prerequisites
Python 3.10+

MiniLibX dependencies (X11/Metal)
```txt
mlx-2.2-py3-none-any.whl
```

#### Installation & Execution
```bash
# Setup virtual environment and install dependencies (webcolors, etc.)
make install 
# Execute the simulation with the default map
make run 
# Full cleanup of environment and cache
make fclean
```

#### Map Configuration
To test different topologies, modify the file_path in flyin.py:
```python
file_path = "maps/easy/03_basic_capacity.txt"
```


## Resource:
- DSA: https://www.w3schools.com/dsa/index.php
- Graph theory: https://www.w3schools.com/python/python_dsa_graphs.asp
- Algorithms: https://medium.com/omarelgabrys-blog/path-finding-algorithms-f65a8902eb40

## Algorithm
1. Pathfinding StrategyThe system utilizes Depth-First Search (DFS) to map all viable routes, calculating a custom "Weighted Cost" for each:$$\text{Cost} = \frac{\text{Zone Cost}}{\min(\text{Zone Capacity}, \text{Link Capacity})}$$

    Routes are then sorted via a Multi-Level Priority Queue:
    1. Type-Specific Priority: Priority zones are moved to the top of the routing table.
    2. Efficiency Sort: Paths are secondary-sorted by the calculated weighted cost.

2. The "Transaction" Movement Algorithm
    To solve the "Order Bias" and "Throughput" challenges, the movement logic follows a Three-Phase 
    Atomic Update:
    1. Predictive Clearing (Look-Ahead): Identifies zones that will be vacated in the current tick, enabling "tailgating" (drones moving into a spot exactly as another leaves).
    2. Pessimistic Reservation: When a drone enters a link, it immediately populates the link AND reserves capacity at the target hub. This prevents "Race Conditions" where two drones might target the same spot from different links.
    3. Commit Phase: Once the travel cost is met, the link is freed, and the drone's position is formally updated to the hub.

## Visual representation
Visual representation are done using MLX library. IT show the whole structure of the map, which is hard to figure out just by the map text. It position all the drones to this map and as i continue moving the drones, drones positions also changes in the map to give a visual understanding on how the drones are moving in real type. To make the simulation more understandable, i have implemented addition visualization shich shows how many drones moved at each step and how much steps each indivisual drones have to take to rache goal.
I have implemented option to to the animation step by sytep by pressing 1, or if user want then can press 2 to automate the animation and press 3 to steop the animation. by pressing 4 we can close the visualizer.
to make things little more dynamics, i have created small hovering motion of the drones while thay are standing on the station.

## AI usages
Ai is used to understand the DFS algorithm and how this kind of problem is solved in real world
doc strings are genereated using gemini
readme file is polished using gemini
All the parsing, algorithem and visualization is implemented myself.