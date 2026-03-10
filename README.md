*This project has been created as part of the 42 curriculum by sudas*
# FLYIN

### Description:
FLYIN is a discrete-event simulation designed to optimize drone swarm throughput across complex, constraint-heavy directed graphs. The project implements a custom resource-reservation algorithm to manage concurrent movement, ensuring no capacity overflows while maximizing the flow of agents from start to goal.

#### Features
- **Concurrent Flow Management:** Handles multi-agent pathfinding with strict hub and link capacity constraints.
- **Priority-Aware Routing:** Intelligently prioritizes specialized paths (e.g., Restricted or Priority zones) without compromising global throughput.
- **Real-Time MLX Visualization:** A custom-built graphical engine using MiniLibX, featuring:
  - Double-Buffered Rendering: Smooth, flicker-free animations.
  - State Monitoring: Real-time display of hub occupancy and individual drone progress.
  - Dynamic Animations: Procedural hovering effects and linear interpolation (LERP) for movement.
- **Interactive Controls:**
  1: Step-by-step manual simulation.
  2: Fully automated real-time animation.
  3: Pause simulation.
  4: Terminate visualizer.

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
To test different maps, modify the file_path in flyin.py present at root directory:
```python
file_path = "maps/easy/03_basic_capacity.txt"
```


## Resource:
- DSA: https://www.w3schools.com/dsa/index.php
- Graph theory: https://www.w3schools.com/python/python_dsa_graphs.asp
- Algorithms: https://medium.com/omarelgabrys-blog/path-finding-algorithms-f65a8902eb40

## Algorithm
1. Pathfinding StrategyThe system utilizes Depth-First Search (DFS) to map all viable routes, calculating a custom "Weighted Cost" for each:$$\text{{Cost}} = \frac{\text{Zone Cost}}{\min(\text{Zone Capacity}, \text{Link Capacity})}$$

    Routes are then sorted via a Multi-Level Priority Queue:
    1. **Type-Specific Priority:** Priority zones are moved to the top of the routing table.
    2. **Efficiency Sort:** Paths are secondary-sorted by the calculated weighted cost.

2. The "Transaction" Movement Algorithm
    To solve the "Order Bias" and "Throughput" challenges, the movement logic follows a Three-Phase 
    Atomic Update:
    1. **Predictive Clearing (Look-Ahead):** Identifies zones that will be vacated in the current tick, enabling "tailgating" (drones moving into a spot exactly as another leaves).
    2. **Pessimistic Reservation:** When a drone enters a link, it immediately populates the link AND reserves capacity at the target hub. This prevents "Race Conditions" where two drones might target the same spot from different links.
    3. **Commit Phase:** Once the travel cost is met, the link is freed, and the drone's position is formally updated to the hub.

## Visual Representation & Graphics EngineThe
Visualization is built on a custom Double-Buffered Rendering Pipeline using the MiniLibX library. Rather than using high-level draw calls that are CPU-intensive in Python, the engine interacts directly with the Frame Buffer to ensure smooth performance even with a high number of active agents.

1. **The Rendering Pipeline (Atomic Frame Updates)**

    To prevent flickering and "ghosting" (trails left by moving drones), the engine follows a strict Clear-Draw-Swap cycle every frame:
    - **Static Layer (Background):** The map topology (Hubs and Links) is "baked" into a static image buffer once during initialization.
    - **Dynamic Layer (Active Buffer):** At the start of every frame, the static background is copied into the active buffer using Fast Memory Slicing (buffer[:] = static[:]). This is significantly faster than re-drawing lines and squares every tick.
    - **Agent Layer:** Drone positions are calculated using Linear Interpolation (LERP) between their last_pos and target_pos. This transforms discrete algorithmic steps into fluid, continuous motion.

2. **Optimization Techniques**
    - **Bulk Memory Manipulation:** To bypass the "Python loop bottleneck," the engine uses byte-multiplication for background clearing and row-based slicing for image blitting. This shifts the heavy lifting from the Python interpreter to optimized C-libraries.
    - **Procedural Animation:** Drones utilize a Sine-Wave Generator to create a subtle "hovering" effect while docked at hubs. This provides immediate visual feedback that the simulation is alive, even when traffic is stalled.
    - **Sprite Blitting with Transparency:** Drones and UI elements are stored as specialized ImgData structures. The engine uses a custom "Blitter" that copies these sprites into the main frame buffer at specific $(x, y)$ offsets.

3. **Real-Time HUD & Telemetry**
    The visualizer acts as a real-time debugger by projecting the internal state of the AdvanceSimulator onto the GUI:
    - **Occupancy Monitors:** Each hub displays a live counter (Capacity : Occupancy).
    Path Highlighting: Links are color-coded based on their type (Priority, Restricted, or Blocked) to show the "Search Space" the drones are navigating.
    - **Drone Metadata:** Each drone is labeled with its ID and current destination, allowing for the immediate identification of bottlenecks or "starvation" issues.

4. **User Interaction & ControlThe engine implements an Event-Driven Hook System:**
    - **Loop Hooks:** Used for the continuous animation of hovering and LERP movement.
    - **Key Hooks:** Allows the user to toggle between Manual Stepping (for debugging logic) and Automated Flow (for observing throughput).

## AI usages
Ai is used to understand the DFS algorithm and how this kind of problem is solved in real world
doc strings are genereated using gemini
readme file is polished using gemini
All the parsing, algorithem and visualization is implemented myself.